import { useParams } from "react-router-dom";
import ProfileEditForm from "../components/ProfileEditForm";

export default function ProfileEditPage() {
    const { username } = useParams();

    const user = {
        username,
        name: "Test User",
        bio: "Lorem ipsum..."
    };

    return <ProfileEditForm user={user} />;
}