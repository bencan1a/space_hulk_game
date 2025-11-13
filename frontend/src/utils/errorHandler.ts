import { AxiosError } from 'axios'
import type { ApiError } from '../services/types'

export class AppError extends Error {
  code: string
  userMessage: string
  retryPossible: boolean
  status?: number

  constructor(
    code: string,
    message: string,
    userMessage: string,
    retryPossible: boolean = false,
    status?: number
  ) {
    super(message)
    this.name = 'AppError'
    this.code = code
    this.userMessage = userMessage
    this.retryPossible = retryPossible
    this.status = status
  }
}

export function handleApiError(error: AxiosError): AppError {
  if (error.response) {
    // Server responded with error
    const status = error.response.status
    const errorData = error.response.data as ApiError | undefined

    if (errorData?.user_message) {
      return new AppError(
        errorData.code,
        errorData.message,
        errorData.user_message,
        errorData.retry_possible,
        status
      )
    }

    // Default error messages by status code
    switch (status) {
      case 400:
        return new AppError(
          'BAD_REQUEST',
          error.message,
          'Invalid request. Please check your input and try again.',
          false,
          status
        )
      case 404:
        return new AppError(
          'NOT_FOUND',
          error.message,
          'The requested resource was not found.',
          false,
          status
        )
      case 500:
        return new AppError(
          'SERVER_ERROR',
          error.message,
          'A server error occurred. Please try again later.',
          true,
          status
        )
      case 503:
        return new AppError(
          'SERVICE_UNAVAILABLE',
          error.message,
          'The service is temporarily unavailable. Please try again.',
          true,
          status
        )
      default:
        return new AppError(
          'UNKNOWN_ERROR',
          error.message,
          'An unexpected error occurred. Please try again.',
          true,
          status
        )
    }
  } else if (error.request) {
    // Request made but no response
    return new AppError(
      'NETWORK_ERROR',
      'No response from server',
      'Unable to connect to the server. Please check your internet connection.',
      true
    )
  } else {
    // Error in request setup
    return new AppError(
      'REQUEST_ERROR',
      error.message,
      'An error occurred while making the request. Please try again.',
      true
    )
  }
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof AppError) {
    return error.userMessage
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'An unknown error occurred'
}
