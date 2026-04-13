"""Unicode payload encoding for invisible instruction injection.

Each encoder takes plaintext instructions and produces a string that is
invisible (or near-invisible) when rendered, but may be interpreted by
an LLM tokenizer as readable text.
"""

from __future__ import annotations

# Mapping of Latin lowercase/uppercase + digits + common punctuation to
# Cyrillic/Greek homoglyphs. Only characters with convincing visual
# equivalents are included.
_HOMOGLYPH_MAP: dict[str, str] = {
    "a": "\u0430",  # Cyrillic а
    "c": "\u0441",  # Cyrillic с
    "d": "\u0501",  # Cyrillic д (komi de)
    "e": "\u0435",  # Cyrillic е
    "h": "\u04bb",  # Cyrillic һ
    "i": "\u0456",  # Cyrillic і
    "j": "\u0458",  # Cyrillic ј
    "o": "\u043e",  # Cyrillic о
    "p": "\u0440",  # Cyrillic р
    "q": "\u051b",  # Cyrillic қ (with descender)
    "s": "\u0455",  # Cyrillic ѕ
    "x": "\u0445",  # Cyrillic х
    "y": "\u0443",  # Cyrillic у
    "A": "\u0410",  # Cyrillic А
    "B": "\u0412",  # Cyrillic В
    "C": "\u0421",  # Cyrillic С
    "E": "\u0415",  # Cyrillic Е
    "H": "\u041d",  # Cyrillic Н
    "I": "\u0406",  # Cyrillic І
    "J": "\u0408",  # Cyrillic Ј
    "K": "\u041a",  # Cyrillic К
    "M": "\u041c",  # Cyrillic М
    "O": "\u041e",  # Cyrillic О
    "P": "\u0420",  # Cyrillic Р
    "S": "\u0405",  # Cyrillic Ѕ
    "T": "\u0422",  # Cyrillic Т
    "X": "\u0425",  # Cyrillic Х
    "Y": "\u04ae",  # Cyrillic Ү
}

# Unicode tag character offset: tag block starts at U+E0000,
# and printable ASCII (0x20-0x7E) maps to U+E0020-U+E007E.
_TAG_OFFSET = 0xE0000


class PayloadEncoder:
    """Encodes plaintext instructions into invisible Unicode sequences."""

    @staticmethod
    def unicode_tags(text: str) -> str:
        """Encode ASCII text as U+E0020-U+E007E tag characters.

        Tag characters are defined in the Unicode Tags block (U+E0000-U+E007F).
        They are invisible in all known renderers (terminals, editors, browsers)
        but some LLM tokenizers decode them back to their ASCII equivalents.

        Only printable ASCII (0x20-0x7E) is encoded. Non-ASCII characters are
        silently dropped.
        """
        result = []
        for ch in text:
            code = ord(ch)
            if 0x20 <= code <= 0x7E:
                result.append(chr(_TAG_OFFSET + code))
            # Non-printable / non-ASCII silently skipped
        return "".join(result)

    @staticmethod
    def zero_width(text: str) -> str:
        """Encode text as binary using zero-width characters.

        Each byte of the UTF-8 encoding is represented as 8 zero-width
        characters:
          - ZWS  (U+200B) = 0
          - ZWNJ (U+200C) = 1

        A Word Joiner (U+2060) separates each byte for unambiguous decoding.
        """
        zws = "\u200b"   # zero-width space = 0
        zwnj = "\u200c"  # zero-width non-joiner = 1
        sep = "\u2060"    # word joiner = byte separator

        encoded_bytes = text.encode("utf-8")
        parts = []
        for byte in encoded_bytes:
            bits = []
            for i in range(7, -1, -1):
                bits.append(zwnj if (byte >> i) & 1 else zws)
            parts.append("".join(bits))
        return sep.join(parts)

    @staticmethod
    def homoglyphs(text: str) -> str:
        """Replace Latin characters with visually identical Cyrillic/Greek equivalents.

        Unlike tag and zero-width encodings, homoglyphs are *visible* but
        appear identical to the original text in most fonts. The model sees
        different Unicode codepoints, which may alter tokenization and
        interpretation.

        Characters without a homoglyph mapping are passed through unchanged.
        """
        return "".join(_HOMOGLYPH_MAP.get(ch, ch) for ch in text)

    @staticmethod
    def variation_selectors(text: str, carrier: str = "") -> str:
        """Encode text using variation selectors appended to carrier characters.

        Uses VS1–VS16 (U+FE00–U+FE0F) to encode 4 bits per carrier character.
        Each ASCII byte is split into two nibbles, each mapped to a variation
        selector appended to a carrier character.

        Requires a carrier string at least 2× the length of the payload.
        If the carrier is too short, it is repeated. Variation selectors are
        invisible in rendering — they normally select glyph variants but have
        no visible effect on most characters.
        """
        if not carrier:
            carrier = " " * (len(text) * 2)  # spaces as minimal carrier

        encoded_bytes = text.encode("utf-8")
        # Each byte needs 2 carrier chars (high nibble + low nibble)
        needed = len(encoded_bytes) * 2
        while len(carrier) < needed:
            carrier = carrier + carrier

        result = []
        byte_idx = 0
        for byte in encoded_bytes:
            high = (byte >> 4) & 0x0F  # 0-15
            low = byte & 0x0F          # 0-15

            # Append carrier char + VS for high nibble
            result.append(carrier[byte_idx * 2])
            result.append(chr(0xFE00 + high))

            # Append carrier char + VS for low nibble
            result.append(carrier[byte_idx * 2 + 1])
            result.append(chr(0xFE00 + low))

            byte_idx += 1

        # Append any remaining carrier chars unchanged
        remaining = carrier[needed:]
        result.append(remaining)

        return "".join(result)

    @staticmethod
    def plaintext(text: str) -> str:
        """No encoding — returns the text as-is.

        Used for decoder priming: placing a visible hint in one surface
        while the actual invisible payload goes in another.
        """
        return text

    @classmethod
    def encode(cls, text: str, encoding: str, carrier: str = "") -> str:
        """Encode a payload using the named encoding technique.

        Args:
            text: The plaintext instruction to hide.
            encoding: One of "unicode_tags", "zero_width", "homoglyphs",
                      "variation_selectors", "plaintext".
            carrier: Visible text to attach the payload to. For tag and
                     zero-width encodings the payload is appended after
                     the carrier. For homoglyphs, carrier is ignored
                     (the text itself is the carrier). For variation
                     selectors, the payload is interleaved into the
                     carrier characters.

        Returns:
            The carrier text with the invisible payload embedded.

        Raises:
            ValueError: If encoding is not recognised.
        """
        encoders = {
            "unicode_tags": cls.unicode_tags,
            "zero_width": cls.zero_width,
            "homoglyphs": cls.homoglyphs,
            "variation_selectors": cls.variation_selectors,
            "plaintext": cls.plaintext,
        }
        encoder = encoders.get(encoding)
        if encoder is None:
            raise ValueError(
                f"Unknown encoding {encoding!r}. "
                f"Available: {', '.join(sorted(encoders))}"
            )

        if encoding == "homoglyphs":
            return encoder(text)
        elif encoding == "plaintext":
            if carrier:
                return carrier + "\n" + encoder(text)
            return encoder(text)
        elif encoding == "variation_selectors":
            return encoder(text, carrier=carrier)
        else:
            # Invisible encodings: append after carrier text
            return carrier + encoder(text)


class PayloadDecoder:
    """Decode invisible payloads back to plaintext (for testing/verification)."""

    @staticmethod
    def unicode_tags(encoded: str) -> str:
        """Decode tag characters back to ASCII."""
        result = []
        for ch in encoded:
            code = ord(ch)
            if _TAG_OFFSET + 0x20 <= code <= _TAG_OFFSET + 0x7E:
                result.append(chr(code - _TAG_OFFSET))
        return "".join(result)

    @staticmethod
    def zero_width(encoded: str) -> str:
        """Decode zero-width binary encoding back to text."""
        zws = "\u200b"
        zwnj = "\u200c"
        sep = "\u2060"

        # Split by byte separator
        byte_groups = encoded.split(sep)
        decoded_bytes = []
        for group in byte_groups:
            if not group:
                continue
            byte_val = 0
            bit_pos = 7
            for ch in group:
                if ch == zwnj:
                    byte_val |= (1 << bit_pos)
                elif ch == zws:
                    pass  # 0 bit, already 0
                else:
                    continue  # skip non-encoding chars
                bit_pos -= 1
            decoded_bytes.append(byte_val)
        return bytes(decoded_bytes).decode("utf-8", errors="replace")

    @staticmethod
    def variation_selectors(encoded: str) -> str:
        """Decode variation-selector-encoded text."""
        # Extract VS codepoints (U+FE00-U+FE0F), pair them as nibbles
        nibbles = []
        for ch in encoded:
            code = ord(ch)
            if 0xFE00 <= code <= 0xFE0F:
                nibbles.append(code - 0xFE00)

        # Pair nibbles into bytes
        decoded_bytes = []
        for i in range(0, len(nibbles) - 1, 2):
            byte_val = (nibbles[i] << 4) | nibbles[i + 1]
            decoded_bytes.append(byte_val)

        return bytes(decoded_bytes).decode("utf-8", errors="replace")

    @staticmethod
    def homoglyphs(encoded: str) -> str:
        """Reverse homoglyph substitution back to Latin."""
        reverse_map = {v: k for k, v in _HOMOGLYPH_MAP.items()}
        return "".join(reverse_map.get(ch, ch) for ch in encoded)
