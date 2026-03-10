import json
from django import template

register = template.Library()

DAY_MAPPING = {
    'Mon': 'Monday',
    'Tue': 'Tuesday',
    'Wed': 'Wednesday',
    'Thu': 'Thursday',
    'Fri': 'Friday',
    'Sat': 'Saturday',
    'Sun': 'Sunday',
}


@register.filter
def format_opening_hours(opening_hours_dict):
    """
    Convert database opening hours format to schema.org OpeningHoursSpecification JSON.
    
    Input format:
    {
        'Mon': {'open': '08:00', 'close': '18:00', 'is_closed': False},
        'Tue': {'open': '08:00', 'close': '18:00', 'is_closed': False},
        ...
    }
    
    Output: JSON array of OpeningHoursSpecification objects
    """
    if not opening_hours_dict:
        return '[]'
    
    if isinstance(opening_hours_dict, str):
        try:
            opening_hours_dict = json.loads(opening_hours_dict)
        except (json.JSONDecodeError, TypeError):
            return '[]'
    
    if not isinstance(opening_hours_dict, dict):
        return '[]'
    
    specs = []
    for day_short, details in opening_hours_dict.items():
        if isinstance(details, dict):
            is_closed = details.get('is_closed', False)
            
            day_long = DAY_MAPPING.get(day_short)
            if not day_long:
                continue
            
            if not is_closed:
                spec = {
                    '@type': 'OpeningHoursSpecification',
                    'dayOfWeek': day_long,
                    'opens': details.get('open', '00:00'),
                    'closes': details.get('close', '23:59'),
                }
                specs.append(spec)
    
    # Return as JSON string (safe for template rendering)
    return json.dumps(specs)
