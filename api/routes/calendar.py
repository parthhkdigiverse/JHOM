"""
Calendar Routes - MongoDB/Beanie Version
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from typing import List, Optional
from beanie import PydanticObjectId

from database.models import CalendarEvent, Admin
from schemas.calendar import CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse
from utils.auth import get_current_admin

router = APIRouter()

# ==================== CREATE EVENT ====================

@router.post("/events", response_model=CalendarEventResponse, status_code=201)
async def create_calendar_event(
    event: CalendarEventCreate,
    current_admin: Admin = Depends(get_current_admin)
):
    """Create new calendar event in MongoDB"""
    
    # Parse datetime - support multiple formats
    def parse_datetime(dt_str: str):
        # Remove 'T' and convert to space format
        dt_str = dt_str.replace('T', ' ')
        
        formats = [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue
        
        raise HTTPException(
            status_code=400,
            detail=f"Invalid datetime format: {dt_str}. Use: YYYY-MM-DD HH:MM"
        )
    
    try:
        start_time = parse_datetime(event.start_time)
        end_time = parse_datetime(event.end_time)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing datetime: {str(e)}")
    
    # Validate times
    if end_time <= start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    
    # Prevent events longer than 24 hours
    if (end_time - start_time).total_seconds() > 24 * 3600:
        raise HTTPException(
            status_code=400,
            detail="Events cannot be longer than 24 hours. Please create separate events."
        )
    
    # Create event
    db_event = CalendarEvent(
        admin_id=current_admin,
        title=event.title,
        event_type=event.event_type,
        start_time=start_time,
        end_time=end_time,
        description=event.description,
        location=event.location,
        status="scheduled"
    )
    
    await db_event.insert()
    return db_event

# ==================== GET EVENTS FOR FULLCALENDAR ====================

@router.get("/events/fullcalendar")
async def get_events_fullcalendar(
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get events in FullCalendar format from MongoDB"""
    
    query = CalendarEvent.find(CalendarEvent.admin_id.id == current_admin.id)
    
    if start:
        try:
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            query = query.find(CalendarEvent.start_time >= start_dt)
        except:
            pass
    
    if end:
        try:
            end_dt = datetime.strptime(end, "%Y-%m-%d")
            query = query.find(CalendarEvent.start_time <= end_dt)
        except:
            pass
    
    events = await query.to_list()
    
    # Color mapping
    colors = {
        "appointment": "#3788d8",
        "meeting": "#f59e0b",
        "work": "#10b981",
        "task": "#ef4444",
        "event": "#8b5cf6"
    }
    
    calendar_events = []
    
    for e in events:
        start_iso = e.start_time.strftime("%Y-%m-%dT%H:%M:%S")
        end_iso = e.end_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        event_data = {
            "id": str(e.id),
            "title": e.title,
            "start": start_iso,
            "end": end_iso,
            "allDay": False,
            "backgroundColor": colors.get(e.event_type, "#3788d8"),
            "borderColor": colors.get(e.event_type, "#3788d8"),
            "textColor": "#ffffff",
            "extendedProps": {
                "description": e.description,
                "event_type": e.event_type,
                "location": e.location,
                "status": e.status
            }
        }
        
        calendar_events.append(event_data)
    
    return calendar_events

@router.get("/events", response_model=List[CalendarEventResponse])
async def get_calendar_events(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get all calendar events from MongoDB"""
    
    query = CalendarEvent.find(CalendarEvent.admin_id.id == current_admin.id)
    
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.find(CalendarEvent.start_time >= start)
        except:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            end = end.replace(hour=23, minute=59, second=59)
            query = query.find(CalendarEvent.end_time <= end)
        except:
            pass
    
    if event_type:
        query = query.find(CalendarEvent.event_type == event_type.lower())
    
    return await query.sort("start_time").to_list()

@router.get("/events/{event_id}", response_model=CalendarEventResponse)
async def get_calendar_event(
    event_id: PydanticObjectId,
    current_admin: Admin = Depends(get_current_admin)
):
    """Get specific event from MongoDB"""
    
    event = await CalendarEvent.find_one(
        CalendarEvent.id == event_id,
        CalendarEvent.admin_id.id == current_admin.id
    )
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event

@router.put("/events/{event_id}", response_model=CalendarEventResponse)
async def update_calendar_event(
    event_id: PydanticObjectId,
    event_update: CalendarEventUpdate,
    current_admin: Admin = Depends(get_current_admin)
):
    """Update event in MongoDB"""
    
    db_event = await CalendarEvent.find_one(
        CalendarEvent.id == event_id,
        CalendarEvent.admin_id.id == current_admin.id
    )
    
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_data = event_update.model_dump(exclude_unset=True)
    
    # Parse datetime if provided
    if 'start_time' in update_data:
        try:
            dt_str = update_data['start_time'].replace('T', ' ')
            update_data['start_time'] = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except:
            raise HTTPException(status_code=400, detail="Invalid start_time format")
    
    if 'end_time' in update_data:
        try:
            dt_str = update_data['end_time'].replace('T', ' ')
            update_data['end_time'] = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except:
            raise HTTPException(status_code=400, detail="Invalid end_time format")
    
    for field, value in update_data.items():
        setattr(db_event, field, value)
    
    db_event.updated_at = datetime.utcnow()
    await db_event.save()
    return db_event

@router.delete("/events/{event_id}", status_code=204)
async def delete_calendar_event(
    event_id: PydanticObjectId,
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete event from MongoDB"""
    
    db_event = await CalendarEvent.find_one(
        CalendarEvent.id == event_id,
        CalendarEvent.admin_id.id == current_admin.id
    )
    
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    await db_event.delete()
    return None

@router.get("/events/today/list")
async def get_today_events(
    current_admin: Admin = Depends(get_current_admin)
):
    """Get today's events from MongoDB"""
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    events = await CalendarEvent.find(
        CalendarEvent.admin_id.id == current_admin.id,
        CalendarEvent.start_time >= today_start,
        CalendarEvent.start_time < today_end,
        CalendarEvent.status == "scheduled"
    ).sort("start_time").to_list()
    
    return {
        "status": "success",
        "date": today_start.strftime("%Y-%m-%d"),
        "total": len(events),
        "events": [
            {
                "id": str(e.id),
                "title": e.title,
                "event_type": e.event_type,
                "start_time": e.start_time.strftime("%H:%M"),
                "end_time": e.end_time.strftime("%H:%M"),
                "location": e.location
            }
            for e in events
        ]
    }

@router.get("/events/upcoming/list")
async def get_upcoming_events(
    days: int = Query(7, ge=1, le=30),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get upcoming events from MongoDB"""
    
    now = datetime.utcnow()
    future = now + timedelta(days=days)
    
    events = await CalendarEvent.find(
        CalendarEvent.admin_id.id == current_admin.id,
        CalendarEvent.start_time >= now,
        CalendarEvent.start_time <= future,
        CalendarEvent.status == "scheduled"
    ).sort("start_time").to_list()
    
    return {
        "status": "success",
        "total": len(events),
        "events": [
            {
                "id": str(e.id),
                "title": e.title,
                "event_type": e.event_type,
                "start_time": e.start_time.isoformat(),
                "location": e.location
            }
            for e in events
        ]
    }