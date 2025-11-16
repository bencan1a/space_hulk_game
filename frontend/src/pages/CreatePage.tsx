import { TemplateGallery } from '../components/generation/TemplateGallery'
import type { TemplateMetadata } from '../services/types'

function CreatePage() {
  const handleTemplateSelect = (template: TemplateMetadata) => {
    console.log('Template selected:', template)
    // TODO: Navigate to next step or store selection
  }

  const handleCustomPrompt = (prompt: string) => {
    console.log('Custom prompt submitted:', prompt)
    // TODO: Navigate to next step or store prompt
  }

  return (
    <div className="page">
      <TemplateGallery onTemplateSelect={handleTemplateSelect} onCustomPrompt={handleCustomPrompt} />
    </div>
  )
}

export default CreatePage
