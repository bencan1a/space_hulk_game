import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import LibraryPage from './pages/LibraryPage'
import CreatePage from './pages/CreatePage'
import PlayPage from './pages/PlayPage'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/library" element={<LibraryPage />} />
          <Route path="/create" element={<CreatePage />} />
          <Route path="/play/:id" element={<PlayPage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
