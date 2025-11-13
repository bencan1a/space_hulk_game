import { Link } from 'react-router-dom'

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <h1>Space Hulk Game</h1>
        <nav>
          <Link to="/">Home</Link>
          <Link to="/library">Library</Link>
          <Link to="/create">Create</Link>
        </nav>
      </div>
    </header>
  )
}

export default Header
