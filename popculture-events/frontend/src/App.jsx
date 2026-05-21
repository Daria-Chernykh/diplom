import { BrowserRouter } from "react-router-dom";

import { AppRouter } from "./router/AppRouter.jsx";
import { AuthProvider } from "./store/AuthContext.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRouter />
      </AuthProvider>
    </BrowserRouter>
  );
}