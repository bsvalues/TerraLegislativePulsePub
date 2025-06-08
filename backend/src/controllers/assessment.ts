import { Request, Response } from 'express';
import { AssessmentService } from '../services/assessment';
import { z } from 'zod';

const assessmentService = new AssessmentService();

export const assessmentController = {
  async calculateAssessment(req: Request, res: Response) {
    try {
      const input = {
        propertyId: req.params.propertyId,
        marketValue: req.body.marketValue,
        assessmentDate: new Date(req.body.assessmentDate),
        assessorId: req.user.id,
        notes: req.body.notes,
        adjustments: req.body.adjustments
      };

      const validation = await assessmentService.validateAssessment(input);
      if (!validation.isValid) {
        return res.status(400).json({
          success: false,
          errors: validation.errors
        });
      }

      const result = await assessmentService.calculateAssessment(input);
      res.json({
        success: true,
        data: result
      });
    } catch (error) {
      console.error('Assessment calculation error:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to calculate assessment'
      });
    }
  },

  async getAssessmentHistory(req: Request, res: Response) {
    try {
      const propertyId = req.params.propertyId;
      const history = await assessmentService.getAssessmentHistory(propertyId);
      res.json({
        success: true,
        data: history
      });
    } catch (error) {
      console.error('Assessment history error:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to fetch assessment history'
      });
    }
  },

  async validateAssessment(req: Request, res: Response) {
    try {
      const input = {
        propertyId: req.params.propertyId,
        marketValue: req.body.marketValue,
        assessmentDate: new Date(req.body.assessmentDate),
        assessorId: req.user.id,
        notes: req.body.notes,
        adjustments: req.body.adjustments
      };

      const validation = await assessmentService.validateAssessment(input);
      res.json({
        success: true,
        data: validation
      });
    } catch (error) {
      console.error('Assessment validation error:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to validate assessment'
      });
    }
  }
}; 