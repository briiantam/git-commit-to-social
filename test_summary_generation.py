import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.git_service import GitService
from src.services.openai_service import OpenAIService
from src.services.file_service import FileService
from src.models.database import initialize_db, store_commit, get_todays_commits

def create_sample_commit(commit_id, author, message, files_changed, insertions, deletions, diff_content):
    """Create a sample commit in the database."""
    timestamp = datetime.now().isoformat()
    store_commit(
        commit_id=commit_id,
        author=author,
        message=message,
        timestamp=timestamp,
        files_changed=files_changed,
        insertions=insertions,
        deletions=deletions,
        diff_content=diff_content
    )
    print(f"Created sample commit: {commit_id}")

def test_summary_generation():
    """Test the summary generation with sample commits."""
    print("Initializing database...")
    initialize_db()
    
    print("Creating sample commits...")
    
    create_sample_commit(
        commit_id="abc123",
        author="alviintam",
        message="Add user authentication feature",
        files_changed=["src/auth/login.tsx", "src/auth/register.tsx", "src/api/auth.ts"],
        insertions=120,
        deletions=5,
        diff_content="""File: src/auth/login.tsx
Change type: A

Code added:
```
import React, { useState } from 'react';
import { View, TextInput, Button, Alert } from 'react-native';
import { useAuth } from '../hooks/useAuth';

export const LoginScreen = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  
  const handleLogin = async () => {
    try {
      await login(email, password);
    } catch (error) {
      Alert.alert('Login Failed', error.message);
    }
  };
  
  return (
    <View>
      <TextInput 
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
      />
```

File: src/api/auth.ts
Change type: M

Code added:
```
export const login = async (email: string, password: string) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  
  if (!response.ok) {
    throw new Error('Login failed');
  }
  
  return response.json();
};
```

Code removed:
```
// TODO: Implement authentication
```"""
    )
    
    create_sample_commit(
        commit_id="def456",
        author="alviintam",
        message="Fix data loading issue in home screen",
        files_changed=["components/home/HomeScreen.tsx", "lib/hooks/useDataFetching.ts"],
        insertions=15,
        deletions=8,
        diff_content="""File: components/home/HomeScreen.tsx
Change type: M

Code added:
```
useEffect(() => {
  if (isConnected) {
    fetchData();
  } else {
    setData(cachedData);
    setIsLoading(false);
  }
}, [isConnected]);
```

Code removed:
```
useEffect(() => {
  fetchData();
}, []);
```

File: lib/hooks/useDataFetching.ts
Change type: M

Code added:
```
const fetchWithRetry = async (url, options, retries = 3) => {
  try {
    return await fetch(url, options);
  } catch (error) {
    if (retries > 0) {
      await new Promise(r => setTimeout(r, 1000));
      return fetchWithRetry(url, options, retries - 1);
    }
    throw error;
  }
};
```"""
    )
    
    print("Initializing services...")
    openai_service = OpenAIService()
    file_service = FileService()
    
    print("Getting today's commits...")
    commits = get_todays_commits()
    print(f"Found {len(commits)} commits")
    
    print("Generating summary...")
    summary = openai_service.summarize_commits(commits)
    print("\nGenerated Summary:")
    print("=" * 50)
    print(summary)
    print("=" * 50)
    
    today = datetime.now().strftime("%Y-%m-%d")
    post_text = f"Daily commit summary ({today}):\n\n{summary}"
    filepath = file_service.save_post(post_text)
    print(f"\nSummary saved to: {filepath}")

if __name__ == "__main__":
    test_summary_generation()
