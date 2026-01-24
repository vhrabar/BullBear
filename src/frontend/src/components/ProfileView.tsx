import "./profile.css";

interface Props {
    user: any;
    isSelf: boolean;
}

export default function ProfileView({ user, isSelf }: Props) {
    return (
        <div className="profile-container">
            <div className="profile-header">
                <img src={user.avatarUrl} alt="avatar" className="avatar" />
                <div>
                    <h1 className="profile-name">{user.name}</h1>
                    <p className="profile-email">{user.email}</p>
                </div>
                {isSelf && (
                    <a href={`/profile/${user.username}/edit`} className="edit-btn">
                        Uredi
                    </a>
                )}
            </div>

            <div className="profile-about">
                <h2>O meni</h2>
                <p>{user.bio}</p>
            </div>
        </div>
    );
}