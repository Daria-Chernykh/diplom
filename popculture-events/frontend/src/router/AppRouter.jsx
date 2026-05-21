import { Route, Routes } from "react-router-dom";

import { AppLayout } from "../layouts/AppLayout.jsx";
import { AuthLayout } from "../layouts/AuthLayout.jsx";

import { HomePage } from "../pages/HomePage.jsx";
import { LoginPage } from "../pages/LoginPage.jsx";
import { RegisterPage } from "../pages/RegisterPage.jsx";
import { LegalAcceptancePage } from "../pages/LegalAcceptancePage.jsx";
import { ForbiddenPage } from "../pages/ForbiddenPage.jsx";
import { NotFoundPage } from "../pages/NotFoundPage.jsx";

import { EventCreatePage } from "../pages/EventCreatePage.jsx";
import { EventEditPage } from "../pages/EventEditPage.jsx";
import { EventRegistrationPage } from "../pages/EventRegistrationPage.jsx";

import { EventCatalogPage } from "../pages/events/EventCatalogPage.jsx";
import { EventDetailsPage } from "../pages/events/EventDetailsPage.jsx";
import { EventPastAdminPage } from "../pages/events/EventPastAdminPage.jsx";

import { UserCabinetPage } from "../pages/user/UserCabinetPage.jsx";
import { UserFavoritesPage } from "../pages/user/UserFavoritesPage.jsx";
import { UserRegistrationsPage } from "../pages/user/UserRegistrationsPage.jsx";
import { UserRegistrationArchivePage } from "../pages/user/UserRegistrationArchivePage.jsx";
import { UserNotificationsPage } from "../pages/user/UserNotificationsPage.jsx";

import { OrganizerCabinetPage } from "../pages/organizer/OrganizerCabinetPage.jsx";
import { OrganizerEventsPage } from "../pages/organizer/OrganizerEventsPage.jsx";
import { OrganizerEventsArchivePage } from "../pages/organizer/OrganizerEventsArchivePage.jsx";
import { OrganizerNotificationsPage } from "../pages/organizer/OrganizerNotificationsPage.jsx";
import { RegisteredParticipantsPage } from "../pages/organizer/RegisteredParticipantsPage.jsx";

import { OrganizerPublicPage } from "../pages/organizers/OrganizerPage.jsx";
import { OrganizersListPage } from "../pages/organizers/OrganizersListPage.jsx";

import { AdminCabinetPage } from "../pages/admin/AdminCabinetPage.jsx";
import { AdminComplaintsPage } from "../pages/admin/AdminComplaintsPage.jsx";
import { AdminUsersPage } from "../pages/admin/AdminUsersPage.jsx";
import { AdminOrganizersPage } from "../pages/admin/AdminOrganizersPage.jsx";

import { LegalRequiredRoute } from "./LegalRequiredRoute.jsx";
import { ProtectedRoute } from "./ProtectedRoute.jsx";
import { PublicOnlyRoute } from "./PublicOnlyRoute.jsx";

export function AppRouter() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<HomePage />} />
        <Route path="/events" element={<EventCatalogPage />} />
        <Route path="/catalog" element={<EventCatalogPage />} />
        <Route path="/events/:eventId" element={<EventDetailsPage />} />
        <Route path="/organizers" element={<OrganizersListPage />} />
        <Route path="/organizers/:organizerId" element={<OrganizerPublicPage />} />

        <Route
          path="/legal-acceptance"
          element={
            <LegalRequiredRoute>
              <LegalAcceptancePage />
            </LegalRequiredRoute>
          }
        />

        <Route path="/legal-documents" element={<LegalAcceptancePage readonly />} />
        <Route path="/legal" element={<LegalAcceptancePage readonly />} />

        <Route
          path="/events/:eventId/registration"
          element={
            <ProtectedRoute roles={["user", "organizer", "admin"]}>
              <EventRegistrationPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/events/:eventId/register"
          element={
            <ProtectedRoute roles={["user", "organizer", "admin"]}>
              <EventRegistrationPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/user"
          element={
            <ProtectedRoute roles={["user", "organizer", "admin"]}>
              <UserCabinetPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/user/registrations"
          element={
            <ProtectedRoute roles={["user", "organizer", "admin"]}>
              <UserRegistrationsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/user/registrations/archive"
          element={
            <ProtectedRoute roles={["user", "organizer", "admin"]}>
              <UserRegistrationArchivePage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/user/favorites"
          element={
            <ProtectedRoute roles={["user", "organizer", "admin"]}>
              <UserFavoritesPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/user/notifications"
          element={
            <ProtectedRoute roles={["user", "organizer", "admin"]}>
              <UserNotificationsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/organizer"
          element={
            <ProtectedRoute roles={["organizer", "admin"]}>
              <OrganizerCabinetPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/organizer/events"
          element={
            <ProtectedRoute roles={["organizer", "admin"]}>
              <OrganizerEventsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/organizer/events/create"
          element={
            <ProtectedRoute roles={["organizer", "admin"]}>
              <EventCreatePage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/organizer/events/:eventId/edit"
          element={
            <ProtectedRoute roles={["organizer", "admin"]}>
              <EventEditPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/organizer/events/archive"
          element={
            <ProtectedRoute roles={["organizer", "admin"]}>
              <OrganizerEventsArchivePage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/organizer/notifications"
          element={
            <ProtectedRoute roles={["organizer", "admin"]}>
              <OrganizerNotificationsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/organizer/events/:eventId/participants"
          element={
            <ProtectedRoute roles={["organizer", "admin"]}>
              <RegisteredParticipantsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin"
          element={
            <ProtectedRoute roles={["admin"]}>
              <AdminCabinetPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/complaints"
          element={
            <ProtectedRoute roles={["admin"]}>
              <AdminComplaintsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/events/:eventId/reviews"
          element={
            <ProtectedRoute roles={["admin"]}>
              <EventPastAdminPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/events/:eventId/past"
          element={
            <ProtectedRoute roles={["admin"]}>
              <EventPastAdminPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/users"
          element={
            <ProtectedRoute roles={["admin"]}>
              <AdminUsersPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/organizers"
          element={
            <ProtectedRoute roles={["admin"]}>
              <AdminOrganizersPage />
            </ProtectedRoute>
          }
        />

        <Route path="/forbidden" element={<ForbiddenPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>

      <Route element={<AuthLayout />}>
        <Route
          path="/login"
          element={
            <PublicOnlyRoute>
              <LoginPage />
            </PublicOnlyRoute>
          }
        />

        <Route
          path="/register"
          element={
            <PublicOnlyRoute>
              <RegisterPage />
            </PublicOnlyRoute>
          }
        />
      </Route>
    </Routes>
  );
}