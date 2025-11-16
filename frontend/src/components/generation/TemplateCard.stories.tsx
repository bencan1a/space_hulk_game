import type { Meta, StoryObj } from '@storybook/react'
import { TemplateCard } from './TemplateCard'

const meta = {
  title: 'Generation/TemplateCard',
  component: TemplateCard,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof TemplateCard>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    template: {
      name: 'horror',
      title: 'Gothic Horror',
      description: 'Generate a horror-themed story with atmospheric dread and suspense',
      category: 'horror',
      variables: [
        {
          name: 'setting',
          type: 'string',
          required: true,
          description: 'The primary location or environment for the horror story',
          example: 'abandoned space hulk',
        },
        {
          name: 'threat',
          type: 'string',
          required: true,
          description: 'The primary threat or horror element',
          example: 'genestealers',
        },
      ],
    },
  },
}

export const Selected: Story = {
  args: {
    ...Default.args,
    selected: true,
  },
}

export const WithOptionalVariables: Story = {
  args: {
    template: {
      name: 'rescue',
      title: 'Rescue Mission',
      description: 'A thrilling rescue mission in hostile territory',
      category: 'action',
      variables: [
        {
          name: 'objective',
          type: 'string',
          required: true,
          description: 'The rescue objective',
        },
        {
          name: 'difficulty',
          type: 'string',
          required: false,
          description: 'Mission difficulty',
          default: 'medium',
        },
      ],
    },
  },
}

export const NoRequiredVariables: Story = {
  args: {
    template: {
      name: 'simple',
      title: 'Simple Template',
      description: 'A simple template with no required variables',
      category: 'general',
      variables: [],
    },
  },
}
