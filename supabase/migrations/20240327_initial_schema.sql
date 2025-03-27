-- Create enum for connection types
CREATE TYPE connection_type AS ENUM ('family', 'friend', 'work', 'acquaintance');

-- Create enum for profile types
CREATE TYPE profile_type AS ENUM ('family', 'friends', 'work', 'acquaintances');

-- Use Supabase Auth for users, so we don't need a users table
-- But we'll create a profiles table for each profile type

-- Create common profiles table
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    type profile_type NOT NULL,
    name VARCHAR(255) NOT NULL,
    photo TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, type)
);

-- Create family profiles table
CREATE TABLE family_profiles (
    profile_id UUID PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE,
    phone_number VARCHAR(20),
    email VARCHAR(255),
    date_of_birth DATE,
    whatsapp VARCHAR(20)
);

-- Create friends profiles table
CREATE TABLE friends_profiles (
    profile_id UUID PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE,
    phone_number VARCHAR(20),
    email VARCHAR(255),
    instagram VARCHAR(255),
    snapchat VARCHAR(255)
);

-- Create work profiles table
CREATE TABLE work_profiles (
    profile_id UUID PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE,
    whatsapp VARCHAR(20),
    telegram VARCHAR(255),
    linkedin VARCHAR(255),
    resume TEXT,
    website VARCHAR(255)
);

-- Create acquaintances profiles table
CREATE TABLE acquaintances_profiles (
    profile_id UUID PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE,
    email VARCHAR(255)
);

-- Create connections table
CREATE TABLE connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    connected_user_id UUID NOT NULL,
    connection_type connection_type NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, connected_user_id)
);

-- Create nfc_tokens table
CREATE TABLE nfc_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    profile_type profile_type NOT NULL,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_profiles_user_id ON profiles(user_id);
CREATE INDEX idx_connections_user_id ON connections(user_id);
CREATE INDEX idx_connections_connected_user_id ON connections(connected_user_id);
CREATE INDEX idx_nfc_tokens_user_id ON nfc_tokens(user_id);
CREATE INDEX idx_nfc_tokens_token ON nfc_tokens(token);

-- Enable Row Level Security (RLS)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE family_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE friends_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE work_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE acquaintances_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE nfc_tokens ENABLE ROW LEVEL SECURITY;

-- Create policies
-- Profiles
CREATE POLICY "Users can view their own profiles" ON profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own profiles" ON profiles
    FOR ALL USING (auth.uid() = user_id);

-- Family profiles
CREATE POLICY "Users can view their own family profiles" ON family_profiles
    FOR SELECT USING (
        (SELECT user_id FROM profiles WHERE id = family_profiles.profile_id) = auth.uid()
    );

CREATE POLICY "Users can manage their own family profiles" ON family_profiles
    FOR ALL USING (
        (SELECT user_id FROM profiles WHERE id = family_profiles.profile_id) = auth.uid()
    );

-- Friends profiles
CREATE POLICY "Users can view their own friends profiles" ON friends_profiles
    FOR SELECT USING (
        (SELECT user_id FROM profiles WHERE id = friends_profiles.profile_id) = auth.uid()
    );

CREATE POLICY "Users can manage their own friends profiles" ON friends_profiles
    FOR ALL USING (
        (SELECT user_id FROM profiles WHERE id = friends_profiles.profile_id) = auth.uid()
    );

-- Work profiles
CREATE POLICY "Users can view their own work profiles" ON work_profiles
    FOR SELECT USING (
        (SELECT user_id FROM profiles WHERE id = work_profiles.profile_id) = auth.uid()
    );

CREATE POLICY "Users can manage their own work profiles" ON work_profiles
    FOR ALL USING (
        (SELECT user_id FROM profiles WHERE id = work_profiles.profile_id) = auth.uid()
    );

-- Acquaintances profiles
CREATE POLICY "Users can view their own acquaintances profiles" ON acquaintances_profiles
    FOR SELECT USING (
        (SELECT user_id FROM profiles WHERE id = acquaintances_profiles.profile_id) = auth.uid()
    );

CREATE POLICY "Users can manage their own acquaintances profiles" ON acquaintances_profiles
    FOR ALL USING (
        (SELECT user_id FROM profiles WHERE id = acquaintances_profiles.profile_id) = auth.uid()
    );

-- Connections
CREATE POLICY "Users can view their own connections" ON connections
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own connections" ON connections
    FOR ALL USING (auth.uid() = user_id);

-- NFC tokens
CREATE POLICY "Users can view their own NFC tokens" ON nfc_tokens
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own NFC tokens" ON nfc_tokens
    FOR ALL USING (auth.uid() = user_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to update updated_at on profiles
CREATE TRIGGER update_profiles_updated_at
BEFORE UPDATE ON profiles
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at_column();
