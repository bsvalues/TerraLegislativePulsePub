import { Router } from 'express';
import { assessmentController } from '../controllers/assessment';
import { authenticate } from '../middleware/auth';
import { validateRequest } from '../middleware/validation';
import { z } from 'zod';

const router = Router();

const assessmentSchema = z.object({
  body: z.object({
    marketValue: z.number().positive(),
    assessmentDate: z.string().transform(str => new Date(str)),
    notes: z.string().optional(),
    adjustments: z.array(z.object({
      type: z.string(),
      value: z.number(),
      description: z.string()
    })).optional()
  })
});

router.post(
  '/properties/:propertyId/assessments',
  authenticate,
  validateRequest(assessmentSchema),
  assessmentController.calculateAssessment
);

router.get(
  '/properties/:propertyId/assessments/history',
  authenticate,
  assessmentController.getAssessmentHistory
);

router.post(
  '/properties/:propertyId/assessments/validate',
  authenticate,
  validateRequest(assessmentSchema),
  assessmentController.validateAssessment
);

export const assessmentRoutes = router; 