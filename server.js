import express from 'express'
import cors from 'cors'
import Api from 'botasaurus-desktop-api'

const app = express()
const port = 3000

app.use(cors())
app.use(express.json())

const api = new Api({ createResponseFiles: false })

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() })
})

app.post('/scrape', async (req, res) => {
  try {
    const { queries, country, max_results, enable_reviews_extraction } = req.body
    
    if (!queries || queries.length === 0) {
      return res.status(400).json({ error: 'queries parameter is required' })
    }

    const data = {
      queries: Array.isArray(queries) ? queries : [queries],
      country: country || null,
      business_type: '',
      max_cities: null,
      randomize_cities: true,
      api_key: '',
      enable_reviews_extraction: enable_reviews_extraction || false,
      max_reviews: 20,
      reviews_sort: 'newest',
      reviews_query: '',
      lang: null,
      max_results: max_results || null,
      coordinates: '',
      zoom_level: 14,
    }

    const task = await api.createSyncTask({ 
      data, 
      scraperName: 'google_maps_scraper' 
    })

    res.json({
      success: true,
      result_count: task[0].result_count,
      data: task[0].result
    })

  } catch (error) {
    console.error('Scrape Error:', error)
    res.status(500).json({ error: error.message })
  }
})

app.listen(port, () => {
  console.log(`Botasaurus API server running on port ${port}`)
})