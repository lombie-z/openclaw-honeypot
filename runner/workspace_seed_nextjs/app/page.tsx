import { TaskList } from "@/components/TaskList";

export default function Home() {
  return (
    <main style={{ maxWidth: 600, margin: "0 auto", padding: "2rem" }}>
      <h1>Task Tracker</h1>
      <p>Manage your daily tasks.</p>
      <TaskList />
    </main>
  );
}
