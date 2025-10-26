-- Упрощенная версия без PostGIS
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('admin', 'moderator', 'analyst')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    author_id UUID REFERENCES users(id),
    category VARCHAR(50) CHECK (category IN ('новость', 'инструкция', 'отчет')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE appeals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_name VARCHAR(100),
    user_contact VARCHAR(100),
    type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    -- Заменим GEOGRAPHY на обычные FLOAT для координат
    latitude FLOAT,
    longitude FLOAT,
    status VARCHAR(20) DEFAULT 'новое' CHECK (status IN ('новое', 'в работе', 'решено')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    photo_url VARCHAR(500)
);

CREATE TABLE road_indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator_type VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    measurement_unit VARCHAR(50),
    latitude FLOAT,
    longitude FLOAT,
    timestamp TIMESTAMP NOT NULL,
    source VARCHAR(50) CHECK (source IN ('датчик', 'расчетный', 'статистика ГИБДД'))
);

CREATE TABLE traffic_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) CHECK (event_type IN ('ДТП', 'ремонт', 'перекрытие')),
    description TEXT,
    latitude FLOAT,
    longitude FLOAT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    severity VARCHAR(20) CHECK (severity IN ('низкая', 'средняя', 'высокая'))
);