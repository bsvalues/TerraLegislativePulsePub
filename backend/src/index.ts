import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import { config } from './config';
import { errorHandler } from './middleware/errorHandler';
import { requestLogger } from './middleware/requestLogger';
import { propertyRoutes } from './routes/property';
import { authRoutes } from './routes/auth';
import { documentRoutes } from './routes/documents';
import { assessmentRoutes } from './routes/assessment';
import { connectDB } from './db';
import { setupSwagger } from './utils/swagger';

const app = express();

// Middleware
app.use(helmet());
app.use(cors());
app.use(compression());
app.use(express.json());
app.use(requestLogger);

// Routes
app.use('/api/properties', propertyRoutes);
app.use('/api/auth', authRoutes);
app.use('/api/documents', documentRoutes);
app.use('/api/assessments', assessmentRoutes);

// API Documentation
setupSwagger(app);

// Error Handling
app.use(errorHandler);

// Database Connection
connectDB()
  .then(() => {
    console.log('Database connected successfully');
  })
  .catch((error) => {
    console.error('Database connection failed:', error);
    process.exit(1);
  });

// Start Server
const PORT = config.port || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
}); 