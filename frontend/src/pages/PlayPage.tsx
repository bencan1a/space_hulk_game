import { useParams } from 'react-router-dom'

function PlayPage() {
  const { id } = useParams<{ id: string }>()

  return (
    <div className="page">
      <h2>Play Game</h2>
      <p>Game ID: {id}</p>
      <p>Interactive gameplay interface coming soon...</p>
    </div>
  )
}

export default PlayPage
