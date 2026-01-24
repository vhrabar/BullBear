import { useParams } from "react-router-dom";
import ProfileView from "../components/ProfileView";

export default function ProfilePage() {
    const { username } = useParams();

    // TODO: backedn

    const user = {
        username,
        name: "Test User",
        email: "test@example.com",
        bio: "Lorem ipsum...",
        avatarUrl: "/avatar.png"
    };

    const isSelf = true;

    return (
        <ProfileView user={user} isSelf={isSelf} />
    );
}