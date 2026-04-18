import React, { useState, useEffect } from 'react';
import {
  Container, Typography, TextField, Button, Box, Paper,
  Alert, List, ListItem, ListItemText, Divider, Chip, Stack
} from '@mui/material';
import { Send, Event, Assignment, Category, PriorityHigh } from '@mui/icons-material';

function App() {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    location: '',
    date: '',
    organiser: ''
  });
  const [submitResult, setSubmitResult] = useState(null);
  const [error, setError] = useState(null);
  const [records, setRecords] = useState([]);

  // 状态颜色映射表，符合项目结果定义
  const getStatusColor = (status) => {
    switch (status) {
      case 'APPROVED': return 'success';
      case 'NEEDS REVISION': return 'warning';
      case 'INCOMPLETE': return 'error';
      default: return 'default';
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitResult(null);

    try {
      const response = await fetch('http://localhost:5001/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();
      setSubmitResult(data);
      // 清空表单
      setFormData({ title: '', description: '', location: '', date: '', organiser: '' });
      fetchRecords();
    } catch (err) {
      setError(err.message);
    }
  };

  const fetchRecords = async () => {
    try {
      const response = await fetch('http://localhost:5002/records');
      if (response.ok) {
        const data = await response.json();
        setRecords(data);
      }
    } catch (err) {
      console.error('Failed to fetch records:', err);
    }
  };

  // 模拟事件驱动的后台处理：每 3 秒自动刷新列表，直到看到最终结果
  useEffect(() => {
    fetchRecords();
    const interval = setInterval(fetchRecords, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center" color="primary" sx={{ fontWeight: 'bold' }}>
        <Event sx={{ mr: 1, fontSize: 40, verticalAlign: 'middle' }} />
        Campus Buzz
      </Typography>
      <Typography variant="subtitle1" align="center" color="text.secondary" sx={{ mb: 4 }}>
        Campus Event Submission & Automatic Review System
      </Typography>

      <Paper elevation={4} sx={{ p: 4, mb: 4, borderRadius: 2 }}>
        <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <Assignment sx={{ mr: 1 }} /> Submit New Event
        </Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <TextField
            fullWidth label="Event Title" name="title"
            value={formData.title} onChange={handleChange} required sx={{ mb: 2 }}
          />
          <TextField
            fullWidth label="Description (Min 40 characters)" name="description"
            value={formData.description} onChange={handleChange} multiline rows={3} required
            error={formData.description.length > 0 && formData.description.length < 40}
            helperText={`${formData.description.length}/40 characters minimum`}
            sx={{
              mb: 2,
              '& .MuiInputLabel-outlined.MuiInputLabel-shrink': {
                backgroundColor: 'white',
                padding: '0 8px',
                marginLeft: '-4px'
              }
            }}
          />
          <TextField
            fullWidth label="Location" name="location"
            value={formData.location} onChange={handleChange} required sx={{ mb: 2 }}
          />
          <TextField
            fullWidth label="Date" name="date" type="date"
            value={formData.date} onChange={handleChange} required
            InputLabelProps={{ shrink: true }}
            helperText="Format: YYYY-MM-DD "
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth label="Organiser Name" name="organiser"
            value={formData.organiser} onChange={handleChange} required sx={{ mb: 3 }}
          />
          <Button
            type="submit" variant="contained" color="primary" size="large"
            startIcon={<Send />} fullWidth sx={{ py: 1.5 }}
          >
            Submit for Review
          </Button>
        </Box>
      </Paper>

      {submitResult && (
        <Alert severity="info" sx={{ mb: 4 }}>
          Submission received (ID: {submitResult.id}). The background process is now verifying your event.
        </Alert>
      )}

      <Paper elevation={4} sx={{ p: 4, borderRadius: 2 }}>
        <Typography variant="h5" gutterBottom>
          Recent Submissions
        </Typography>
        {records.length === 0 ? (
          <Typography color="text.secondary">No events submitted yet.</Typography>
        ) : (
          <List>
            {records.map((record, index) => (
              <React.Fragment key={record.id}>
                <ListItem alignItems="flex-start" sx={{ px: 0, py: 2 }}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="h6">{record.title}</Typography>
                        <Chip
                          label={record.status}
                          color={getStatusColor(record.status)}
                          size="small"
                          sx={{ fontWeight: 'bold' }}
                        />
                      </Box>
                    }
                    secondary={
                      <Box component="span">
                        <Typography variant="body2" color="text.primary">
                          {record.location} | {record.date} | {record.organiser}
                        </Typography>

                        <Typography variant="body2" sx={{ fontStyle: 'italic', my: 1 }}>
                          "{record.description}"
                        </Typography>

                        {/* 展示结果详情：分类、优先级和备注。只有当状态不是 PENDING 时才显示这些详细信息  */}
                        {record.status !== 'PENDING' && (
                          <Box sx={{ mt: 1 }}>
                            <Stack direction="row" spacing={1}>
                              <Chip label={`Category: ${record.category}`} size="small" variant="outlined" />
                              <Chip label={`Priority: ${record.priority}`} size="small" variant="outlined" />
                            </Stack>
                            <Alert severity="info" icon={false} sx={{ mt: 1, py: 0 }}>
                              <strong>Note:</strong> {record.note}
                            </Alert>
                          </Box>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
                {index < records.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        )}
      </Paper>
    </Container>
  );
}

export default App;