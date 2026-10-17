// Negative lint fixture: named exports only in *.ts (FRONTEND.md §2 rule 5).
export default function shout(text: string): string {
  return text.toUpperCase()
}
