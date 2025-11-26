<!-- QUICK START GUIDE FOR TASK ANALYZER -->

# Task Analyzer - Quick Reference Guide

## 🚀 Getting Started in 30 Seconds

### Step 1: Start the Backend
```bash
cd task-analyzer
.venv\Scripts\activate
set DJANGO_SETTINGS_MODULE=settings
python manage.py runserver 127.0.0.1:8000 --noreload
```

### Step 2: Open Frontend
- Open `index.html` in your browser
- Or navigate to: `file:///C:/Users/sureshraj/task-analyzer/index.html`

### Step 3: Add Tasks
- Click "Add Individual Task" OR "Bulk Import (JSON)"
- Fill in task details
- Click "➕ Add Task"

### Step 4: Analyze
- Select strategy from dropdown
- Click "🚀 Analyze Tasks"
- View ranked results!

---

## 📋 Task Format

### Individual Task Fields
```
Title:        (required) Task name/description
Priority:     (1-10, required) How important is it?
Effort:       (1-10, required) How much work needed?
Due Date:     (optional) YYYY-MM-DD format
Dependencies: (optional) Comma-separated task IDs
```

### JSON Array Format
```json
[
  {
    "title": "Task name",
    "priority": 8,
    "effort": 4,
    "due_date": "2025-11-30",
    "dependencies": ["task_id_1", "task_id_2"]
  }
]
```

---

## 🎯 Strategies Explained

| Strategy | Icon | Use Case | Algorithm |
|----------|------|----------|-----------|
| Smart Balance | 🧠 | Default, best overall | 40% urgency + 40% importance + 20% effort |
| Fastest Wins | ⚡ | Quick momentum | Only effort component (lower = higher score) |
| High Impact | 🎯 | Strategic focus | Only importance component (priority/10) |
| Deadline Driven | ⏰ | Time-sensitive | Only urgency component (days to deadline) |

---

## 📊 Understanding Results

### Score (0 - 1)
- **0.9-1.0**: Critical - Do immediately
- **0.7-0.9**: High Priority - Do soon
- **0.4-0.7**: Medium Priority - Schedule
- **0.0-0.4**: Low Priority - Defer

### Color Indicators
- 🔴 **Red** (≥0.7): High priority
- 🟠 **Orange** (0.4-0.7): Medium priority
- 🟢 **Green** (<0.4): Low priority

### Components
- **Urgency%**: How close to deadline (0-100%)
- **Importance%**: How critical (0-100%)
- **Effort%**: Efficiency score (0-100%)

---

## 💡 Pro Tips

### Tip 1: Use Smart Balance for Most Cases
- Balances all factors
- Best for realistic prioritization
- Recommended default

### Tip 2: Switch Strategies Based on Context
- Use **Fastest Wins** when you need momentum
- Use **Deadline Driven** for time-critical work
- Use **High Impact** for strategic planning

### Tip 3: Set Dependencies for Related Tasks
```
Task A depends on Task B → Add "task_b_id" to Task A
This helps identify circular dependencies
```

### Tip 4: Use Due Dates for Better Urgency Scoring
- Tasks without due dates get neutral urgency (0.3)
- Overdue tasks get maximum urgency (1.0)
- Deadlines within 3 days get 0.8

### Tip 5: Bulk Import for Multiple Tasks
```bash
Copy tasks from spreadsheet or JSON file
Use "Bulk Import" tab
Paste JSON array
Click "📥 Import JSON"
```

---

## 🔧 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Tab | Navigate form fields |
| Enter | Submit form / Activate button |
| Shift+Tab | Navigate backwards |
| Escape | Clear input field |

---

## ⚠️ Common Issues & Solutions

### Issue: API Connection Error
**Solution**: 
- Check Django server is running
- Verify URL: `http://127.0.0.1:8000`
- Check browser console for errors

### Issue: Tasks Not Saving
**Solution**:
- Check browser storage is enabled
- Clear cache and reload
- Try private/incognito window

### Issue: Unexpected Scores
**Solution**:
- Check priority values (1-10 range)
- Verify due date format (YYYY-MM-DD)
- Look for circular dependencies

### Issue: JSON Import Fails
**Solution**:
- Ensure valid JSON format
- Check all required fields present
- Use provided example format
- Look at error message details

---

## 📈 Example Workflows

### Workflow 1: Quick Task Prioritization
1. Add 5-10 tasks individually
2. Set due dates
3. Click Analyze (Smart Balance)
4. Start with #1 task

### Workflow 2: Large Project Import
1. Export tasks as JSON from spreadsheet
2. Use "Bulk Import" tab
3. Paste JSON array
4. Try different strategies
5. Export results

### Workflow 3: Deadline-Heavy Work
1. Add all tasks with due dates
2. Select "Deadline Driven" strategy
3. Analyze
4. Complete in order

### Workflow 4: Strategic Planning
1. Add high-importance strategic tasks
2. Select "High Impact" strategy
3. Analyze
4. Allocate resources accordingly

---

## 🎨 Customization

### Change API URL
Edit `script.js`:
```javascript
this.apiUrl = 'http://YOUR_SERVER:PORT/api/tasks';
```

### Change Color Theme
Edit `styles.css`:
```css
:root {
    --primary-color: #YOUR_COLOR;
    --secondary-color: #YOUR_COLOR;
    /* ... more colors ... */
}
```

### Add New Strategy
1. Edit backend `scoring.py`
2. Add scoring logic
3. Update frontend dropdown in `index.html`
4. Update strategy info in `script.js`

---

## 📱 Mobile Usage

### Best Practices for Mobile
- ✅ Portrait mode recommended
- ✅ Use bulk import for many tasks
- ✅ Tap strategy dropdown to change
- ✅ Scroll down for full results
- ✅ Use local storage for persistence

### Mobile Optimizations
- Touch-friendly buttons (44px minimum)
- Responsive layout (adapts to screen)
- Readable fonts on all devices
- Fast API responses

---

## 🧪 Testing the App

### Test Case 1: Single Task
1. Add one task
2. Analyze
3. Should show score

### Test Case 2: Multiple Tasks
1. Add 5+ tasks with different priorities
2. Analyze with Smart Balance
3. Check ordering makes sense

### Test Case 3: Different Strategies
1. Add tasks
2. Try each strategy
3. Observe different orderings
4. Compare results

### Test Case 4: JSON Import
1. Copy sample tasks.json
2. Bulk import
3. Verify all tasks imported
4. Analyze results

### Test Case 5: Edge Cases
1. Tasks with no due date
2. Tasks with high effort/low priority
3. Tasks with dependencies
4. Many tasks (50+)

---

## 📚 API Endpoints Reference

### POST /api/tasks/analyze/
```javascript
fetch('http://127.0.0.1:8000/api/tasks/analyze/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tasks: [
      {
        id: "task1",
        title: "Example",
        priority: 8,
        effort: 4,
        due_date: "2025-11-30",
        dependencies: []
      }
    ],
    strategy: "smart"
  })
})
```

### Response Format
```json
{
  "tasks": [
    {
      "id": "task1",
      "score": 0.79,
      "components": {
        "urgency": 0.8,
        "importance_norm": 1.0,
        "effort": 0.33
      }
    }
  ],
  "cycle_detected": false,
  "cycles": []
}
```

---

## 🐛 Debugging

### Enable Console Logs
1. Open browser DevTools (F12)
2. Check Console tab
3. See app initialization message
4. Watch for errors

### Network Tab
1. Open DevTools
2. Network tab
3. Click Analyze
4. Watch API request
5. Check response status

### Storage Tab
1. Open DevTools
2. Storage/Application tab
3. Check localStorage
4. See saved tasks

---

## 🎓 Learning Resources

### For Developers
- `script.js` - Main application logic
- `styles.css` - Design patterns
- Backend `scoring.py` - Algorithm details
- `test_scoring.py` - Testing examples

### For Users
- `index.html` - UI structure
- Form validations - Input patterns
- Strategy descriptions - Use cases

---

## 🔐 Important Notes

### Security
- No sensitive data stored
- All processing client-side
- No authentication required
- Development mode enabled

### Limitations
- ~5000 tasks max recommended
- No user accounts
- No cloud backup
- Browser storage only

### Future Enhancements
- Dark mode toggle
- Custom color themes
- Database persistence
- User accounts
- Collaboration features
- Export to PDF/CSV

---

## 📞 Getting Help

### Check These First
1. **Browser Console** - F12, Console tab
2. **DevTools Network** - See API requests
3. **Error Messages** - Red alerts on screen
4. **Local Storage** - Check saved data

### Debug Steps
1. Clear browser cache
2. Reload page (Ctrl+Shift+R)
3. Check backend server is running
4. Verify API URL is correct
5. Check JSON format in import

### Common Errors
- "Add at least one task" → Add tasks first
- "Invalid JSON" → Check JSON format
- "API Connection Error" → Start backend server
- "Tasks not saving" → Enable localStorage

---

## 📋 Checklist Before Use

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Django migrations run (`python manage.py migrate`)
- [ ] Backend server running (`python manage.py runserver ...`)
- [ ] API accessible on `127.0.0.1:8000`
- [ ] Frontend file opened in browser
- [ ] JavaScript console shows no errors
- [ ] Ready to add tasks!

---

**Last Updated**: November 26, 2025  
**Version**: 1.0.0  
**Maintained By**: Development Team
