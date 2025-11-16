import type { Meta, StoryObj } from '@storybook/react'
import { fn } from '@storybook/test'
import { TemplateGallery } from './TemplateGallery'

const meta = {
  title: 'Generation/TemplateGallery',
  component: TemplateGallery,
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
  args: {
    onTemplateSelect: fn(),
    onCustomPrompt: fn(),
  },
} satisfies Meta<typeof TemplateGallery>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {},
}
