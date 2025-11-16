import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

/**
 * HomePage component that redirects to the Library page.
 *
 * This provides a clean entry point while ensuring users land
 * on the main library interface where they can browse and play games.
 */
function HomePage() {
  const navigate = useNavigate()

  useEffect(() => {
    navigate('/library')
  }, [navigate])

  return null
}

export default HomePage
