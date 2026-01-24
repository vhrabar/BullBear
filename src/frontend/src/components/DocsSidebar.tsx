import { Link } from "react-router-dom";

interface SidebarProps {
  pages: string[];
}

const DocsSidebar: React.FC<SidebarProps> = ({ pages }) => {
  return (
    <aside style={{ width: "200px", padding: "1rem", borderRight: "1px solid #ccc" }}>
      <nav>
        <ul style={{ listStyle: "none", padding: 0 }}>
          {pages.map((page) => (
            <li key={page}>
              <Link to={`/docs/${page}`} style={{ textDecoration: "none" }}>
                {page.charAt(0).toUpperCase() + page.slice(1)}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default DocsSidebar;
