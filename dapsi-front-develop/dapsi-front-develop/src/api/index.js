import axios from 'axios'

const CHATBOT = axios.create({
  baseURL: 'http://165.232.76.158:5005',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
})

export { CHATBOT }