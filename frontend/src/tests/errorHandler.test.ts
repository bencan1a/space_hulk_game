import { describe, it, expect } from 'vitest'
import { handleApiError, AppError, getErrorMessage } from '../utils/errorHandler'
import { AxiosError } from 'axios'
import type { ApiError } from '../services/types'

describe('Error Handler', () => {
  it('should handle API error with user message', () => {
    const apiError: ApiError = {
      code: 'CUSTOM_ERROR',
      message: 'Internal error message',
      user_message: 'User-friendly message',
      retry_possible: true,
    }

    const axiosError = {
      response: {
        status: 500,
        data: apiError,
      },
      message: 'Server Error',
      isAxiosError: true,
    } as AxiosError

    const result = handleApiError(axiosError)

    expect(result).toBeInstanceOf(AppError)
    expect(result.code).toBe('CUSTOM_ERROR')
    expect(result.userMessage).toBe('User-friendly message')
    expect(result.retryPossible).toBe(true)
    expect(result.status).toBe(500)
  })

  it('should handle 400 Bad Request', () => {
    const axiosError = {
      response: {
        status: 400,
        data: {},
      },
      message: 'Bad Request',
      isAxiosError: true,
    } as AxiosError

    const result = handleApiError(axiosError)

    expect(result.code).toBe('BAD_REQUEST')
    expect(result.userMessage).toBe('Invalid request. Please check your input and try again.')
    expect(result.retryPossible).toBe(false)
    expect(result.status).toBe(400)
  })

  it('should handle 404 Not Found', () => {
    const axiosError = {
      response: {
        status: 404,
        data: {},
      },
      message: 'Not Found',
      isAxiosError: true,
    } as AxiosError

    const result = handleApiError(axiosError)

    expect(result.code).toBe('NOT_FOUND')
    expect(result.userMessage).toBe('The requested resource was not found.')
    expect(result.retryPossible).toBe(false)
  })

  it('should handle 500 Server Error', () => {
    const axiosError = {
      response: {
        status: 500,
        data: {},
      },
      message: 'Internal Server Error',
      isAxiosError: true,
    } as AxiosError

    const result = handleApiError(axiosError)

    expect(result.code).toBe('SERVER_ERROR')
    expect(result.userMessage).toBe('A server error occurred. Please try again later.')
    expect(result.retryPossible).toBe(true)
  })

  it('should handle 503 Service Unavailable', () => {
    const axiosError = {
      response: {
        status: 503,
        data: {},
      },
      message: 'Service Unavailable',
      isAxiosError: true,
    } as AxiosError

    const result = handleApiError(axiosError)

    expect(result.code).toBe('SERVICE_UNAVAILABLE')
    expect(result.userMessage).toBe('The service is temporarily unavailable. Please try again.')
    expect(result.retryPossible).toBe(true)
  })

  it('should handle network errors', () => {
    const axiosError = {
      request: {},
      message: 'Network Error',
      isAxiosError: true,
    } as AxiosError

    const result = handleApiError(axiosError)

    expect(result.code).toBe('NETWORK_ERROR')
    expect(result.userMessage).toBe('Unable to connect to the server. Please check your internet connection.')
    expect(result.retryPossible).toBe(true)
  })

  it('should handle request setup errors', () => {
    const axiosError = {
      message: 'Invalid URL',
      isAxiosError: true,
    } as AxiosError

    const result = handleApiError(axiosError)

    expect(result.code).toBe('REQUEST_ERROR')
    expect(result.userMessage).toBe('An error occurred while making the request. Please try again.')
    expect(result.retryPossible).toBe(true)
  })

  it('should get error message from AppError', () => {
    const appError = new AppError('TEST', 'internal', 'User message', false)
    const message = getErrorMessage(appError)
    expect(message).toBe('User message')
  })

  it('should get error message from Error', () => {
    const error = new Error('Test error')
    const message = getErrorMessage(error)
    expect(message).toBe('Test error')
  })

  it('should handle unknown errors', () => {
    const message = getErrorMessage('string error')
    expect(message).toBe('An unknown error occurred')
  })
})
