from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import subprocess

from app.api.v1.deps import get_db, get_current_admin

router = APIRouter()

@router.post('/bundles/generate')
async def generate_exam_bundle(
    bundle_config: Dict[str, Any] = None,
    current_admin = Depends(get_current_admin)
):
    """Generate a new exam bundle (Admin only)"""
    
    try:
        # Run the bundle generator
        result = subprocess.run(
            ['python', '/app/generate_complete_lgs_bundle_v2.py'],
            capture_output=True,
            text=True,
            cwd='/app'
        )
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Generation failed: {result.stderr}")
        
        return {
            'success': True,
            'message': 'New exam bundle generated successfully',
            'output': result.stdout[-1000:],  # Last 1000 chars of output
            'bundle_id': 'lgs-karma-v2'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating bundle: {str(e)}")

@router.get('/analytics/bundles')
async def get_bundle_analytics(
    current_admin = Depends(get_current_admin)
):
    """Get analytics for exam bundles (Admin only)"""
    
    # In a real implementation, this would query the database for usage stats
    return {
        'total_bundles': 1,
        'total_sessions': 0,
        'total_completions': 0,
        'average_score': 0,
        'popular_subjects': [],
        'bundle_usage': {
            'lgs-karma-v2': {
                'sessions': 0,
                'completions': 0,
                'average_score': 0,
                'last_used': None
            }
        }
    }

@router.delete('/bundles/{bundle_id}')
async def delete_bundle(
    bundle_id: str,
    current_admin = Depends(get_current_admin)
):
    """Delete an exam bundle (Admin only)"""
    
    if bundle_id == 'lgs-karma-v2':
        # In a real implementation, you'd delete the bundle files and database records
        return {
            'success': True,
            'message': f'Bundle {bundle_id} marked for deletion'
        }
    
    raise HTTPException(status_code=404, detail="Bundle not found")