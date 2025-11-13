import { ReactNode } from 'react'
import Header from './common/Header'
import Footer from './common/Footer'

interface LayoutProps {
  children: ReactNode
}

function Layout({ children }: LayoutProps) {
  return (
    <div className="app-container">
      <Header />
      <main className="main-content">{children}</main>
      <Footer />
    </div>
  )
}

export default Layout
