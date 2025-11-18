## Frontend Setup

### Prerequisites
- Node.js 18+ and npm/yarn

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:3000`.

### Build

```bash
npm run build
npm start
```

### Project Structure

```
src/
├─ app/
│  ├─ layout.tsx        # Root layout
│  ├─ page.tsx          # Home page
│  ├─ globals.css       # Global styles
│  ├─ student/
│  │  ├─ dashboard/page.tsx     # Student dashboard
│  │  └─ exams/[id]/page.tsx    # Exam interface
│  ├─ teacher/
│  │  └─ dashboard/page.tsx     # Teacher dashboard
│  └─ admin/
│     └─ dashboard/page.tsx     # Admin dashboard
└─ lib/
   ├─ api.ts            # Axios API client
   └─ auth.ts           # Zustand auth store
```

### API Integration

The frontend uses Axios for API calls with automatic JWT token injection. The backend API URL is configurable via `NEXT_PUBLIC_API_URL` environment variable.

Example:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

### Features

- **Student Dashboard**: View exam progress, subject mastery, and recommended topics
- **Exam Interface**: Take adaptive exams with timer and question navigation
- **Teacher Dashboard**: Manage students and assignments
- **Admin Dashboard**: System management and user administration
- **JWT Authentication**: Automatic token handling and 401 redirect
- **TypeScript**: Full type safety with strict mode

### TODO

- [ ] Add authentication pages (login, register)
- [ ] Add UI component library (Tailwind CSS or Material-UI)
- [ ] Implement exam start/submission flows
- [ ] Add loading states and error boundaries
- [ ] Add responsive design and mobile support
- [ ] Add dark mode support
- [ ] Add analytics and tracking
