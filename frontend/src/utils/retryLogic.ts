import { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

export async function retryRequest(
  client: AxiosInstance,
  config: AxiosRequestConfig,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<AxiosResponse> {
  let lastError: Error | null = null

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await client.request(config)
    } catch (error) {
      lastError = error as Error

      if (i < maxRetries - 1) {
        // Exponential backoff
        const waitTime = delay * Math.pow(2, i)
        if (import.meta.env.DEV) {
          console.log(`Retry ${i + 1}/${maxRetries} after ${waitTime}ms...`)
        }
        await new Promise((resolve) => setTimeout(resolve, waitTime))
      }
    }
  }

  throw lastError
}
