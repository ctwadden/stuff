import Link from 'next/link';

const navItems = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/projects/new', label: 'New Project Wizard' },
  { href: '/projects/demo-project', label: 'Project Detail' },
  { href: '/mapper', label: '80/20 Mapper' },
  { href: '/socratic', label: 'Socratic Coach' },
  { href: '/study', label: 'Study Session' },
  { href: '/reviews', label: 'Review Calendar' },
  { href: '/errors', label: 'Error Log' },
];

export function Sidebar() {
  return (
    <aside className="border-r border-slate-800 bg-slate-900 p-4">
      <div className="mb-6">
        <p className="text-sm uppercase tracking-wide text-slate-400">Navigation</p>
      </div>
      <nav className="space-y-2">
        {navItems.map((item) => (
          <Link key={item.href} href={item.href} className="block rounded px-3 py-2 text-sm hover:bg-slate-800">
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
