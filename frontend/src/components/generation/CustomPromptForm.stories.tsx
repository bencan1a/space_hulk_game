import type { Meta, StoryObj } from '@storybook/react'
import { fn } from '@storybook/test'
import { CustomPromptForm } from './CustomPromptForm'

const meta = {
  title: 'Generation/CustomPromptForm',
  component: CustomPromptForm,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  args: {
    onSubmit: fn(),
  },
} satisfies Meta<typeof CustomPromptForm>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {},
}

export const WithInitialValue: Story = {
  args: {
    initialValue:
      'Create a gothic horror text-based adventure game set in an abandoned space hulk with atmospheric dread and suspense',
  },
}

export const WithLongInitialValue: Story = {
  args: {
    initialValue:
      'Create a gothic horror text-based adventure game set in an abandoned space hulk. The game should emphasize atmospheric dread, isolation, and body horror. The player is a lone marine investigating strange signals from a derelict vessel. As they explore the dark corridors, they encounter evidence of a terrible fate that befell the previous crew. The horror should build gradually through environmental storytelling and subtle audio cues.',
  },
}
