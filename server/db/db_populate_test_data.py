#!/usr/bin/env python3
"""
Test data population script for the video search database.
Can be run from the db directory with: python3 populate_test_data.py
"""

import sys
from pathlib import Path
from sqlalchemy import text

# Add the server directory to the Python path so we can import from it
current_dir = Path(__file__).resolve().parent
server_dir = current_dir.parent
if str(server_dir) not in sys.path:
    sys.path.insert(0, str(server_dir))

# Import Flask app and models
from app import create_app
from extensions import db
from db.models import (
    Property, PropertyValue, Video, VideoDescription, 
    VideoPropertyValue, User, Collection, UserCollection, CollectionVideo
)

def populate_test_data():
    """Populate the database with test data."""
    app = create_app()
    
    with app.app_context():
        print("Starting test data population...")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing data...")
        db.session.query(CollectionVideo).delete()
        db.session.query(UserCollection).delete()
        db.session.query(Collection).delete()
        db.session.query(User).delete()
        db.session.query(VideoPropertyValue).delete()
        db.session.query(VideoDescription).delete()
        db.session.query(Video).delete()
        db.session.query(PropertyValue).delete()
        db.session.query(Property).delete()
        db.session.commit()
        
        # Reset sequences to start from 1
        print("Resetting ID sequences...")
        db.session.execute(text("ALTER SEQUENCE property_id_seq RESTART WITH 1"))
        db.session.execute(text("ALTER SEQUENCE property_value_id_seq RESTART WITH 1"))
        db.session.execute(text("ALTER SEQUENCE video_id_seq RESTART WITH 1"))
        db.session.execute(text("ALTER SEQUENCE video_description_id_seq RESTART WITH 1"))
        db.session.execute(text("ALTER SEQUENCE video_property_value_id_seq RESTART WITH 1"))
        db.session.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1"))
        db.session.execute(text("ALTER SEQUENCE collection_id_seq RESTART WITH 1"))
        db.session.execute(text("ALTER SEQUENCE user_collection_id_seq RESTART WITH 1"))
        db.session.execute(text("ALTER SEQUENCE collection_video_id_seq RESTART WITH 1"))
        db.session.commit()
        
        # Create Properties and PropertyValues
        print("Creating Properties and PropertyValues...")
        
        # Create parent properties
        camera_motion = Property(name="camera motion", display_order=1)
        camera_angle = Property(name="camera angle", display_order=2)
        lighting = Property(name="lighting", display_order=3)
        
        db.session.add_all([camera_motion, camera_angle, lighting])
        db.session.commit()  # Commit to get IDs for foreign keys
        
        # Create child properties under camera motion (only pan and tracking)
        pan = Property(name="pan", parent_id=camera_motion.id, display_order=1)
        tracking = Property(name="tracking", parent_id=camera_motion.id, display_order=2)
        
        db.session.add_all([pan, tracking])
        db.session.commit()  # Commit to get IDs for foreign keys
        
        # Create PropertyValues for pan
        pan_left = PropertyValue(property_id=pan.id, value="left", display_order=1)
        pan_right = PropertyValue(property_id=pan.id, value="right", display_order=2)
        
        # Create PropertyValues for tracking
        tracking_aerial = PropertyValue(property_id=tracking.id, value="aerial", display_order=1)
        tracking_tail = PropertyValue(property_id=tracking.id, value="tail", display_order=2)
        tracking_lead = PropertyValue(property_id=tracking.id, value="lead", display_order=3)
        
        # Create PropertyValues directly under camera motion
        camera_motion_dolly_zoom = PropertyValue(property_id=camera_motion.id, value="dolly zoom", display_order=1)
        camera_motion_forward = PropertyValue(property_id=camera_motion.id, value="forward", display_order=2)
        camera_motion_backward = PropertyValue(property_id=camera_motion.id, value="backward", display_order=3)
        
        # Create PropertyValues for camera angle
        angle_high = PropertyValue(property_id=camera_angle.id, value="high", display_order=1)
        angle_low = PropertyValue(property_id=camera_angle.id, value="low", display_order=2)
        
        # Create PropertyValues for lighting
        lighting_sidelight = PropertyValue(property_id=lighting.id, value="sidelight", display_order=1)
        lighting_underlight = PropertyValue(property_id=lighting.id, value="underlight", display_order=2)
        lighting_backlight = PropertyValue(property_id=lighting.id, value="backlight", display_order=3)
        
        # Add all PropertyValues
        property_values = [
            pan_left, pan_right,
            tracking_aerial, tracking_tail, tracking_lead,
            camera_motion_dolly_zoom, camera_motion_forward, camera_motion_backward,
            angle_high, angle_low,
            lighting_sidelight, lighting_underlight, lighting_backlight
        ]
        
        db.session.add_all(property_values)
        db.session.commit()
        
        print(f"Created {len([camera_motion, camera_angle, lighting, pan, tracking])} properties")
        print(f"Created {len(property_values)} property values")
        
        # Create Videos and VideoDescriptions
        print("Creating Videos and VideoDescriptions...")
        
        # Create Videos
        harry_potter_video = Video(
            path="https://www.youtube.com/watch?v=6iCJ7FlkaB8",
            aspect_ratio="16:9",
            genre="Fantasy"
        )
        
        lotr_video = Video(
            path="https://www.youtube.com/watch?v=7lwJOxN_gXc",
            aspect_ratio="16:9", 
            genre="Fantasy"
        )
        
        anime_video = Video(
            path="https://www.youtube.com/watch?v=08kp3Cs31Ow&list=RD08kp3Cs31Ow&start_radio=1",
            aspect_ratio="16:9",
            genre="Action/Superhero Anime"
        )
        
        taylor_swift_video = Video(
            path="https://www.youtube.com/watch?v=e-ORhEE9VVg&list=RDe-ORhEE9VVg&start_radio=1",
            aspect_ratio="16:9",
            genre="Pop Music"
        )
        
        endgame_video = Video(
            path="https://www.youtube.com/watch?v=4pFUP0HZwWM",
            aspect_ratio="16:9",
            genre="Action/Superhero"
        )
        
        videos = [harry_potter_video, lotr_video, anime_video, taylor_swift_video, endgame_video]
        db.session.add_all(videos)
        db.session.commit()  # Commit to get IDs for foreign keys
        
        # Create VideoDescriptions
        # Harry Potter - 1 description
        hp_desc = VideoDescription(
            video_id=harry_potter_video.id,
            description="A magical scene from Harry Potter and the Sorcerer's Stone featuring Hogwarts castle and young wizards.",
            confidence_score=0.85
        )
        
        # LOTR - 2 descriptions
        lotr_desc1 = VideoDescription(
            video_id=lotr_video.id,
            description="Epic fantasy battle scene from The Lord of the Rings with sweeping landscapes.",
            confidence_score=0.92
        )
        lotr_desc2 = VideoDescription(
            video_id=lotr_video.id,
            description="The camera uses dramatic forward tracking movement with cinematic sidelight illuminating the characters.",
            confidence_score=0.78
        )
        
        # Anime - 1 description
        anime_desc = VideoDescription(
            video_id=anime_video.id,
            description="High-energy anime preview trailer featuring superhero action sequences and dynamic animation.",
            confidence_score=0.89
        )
        
        # Taylor Swift - 1 description
        taylor_desc = VideoDescription(
            video_id=taylor_swift_video.id,
            description="Taylor Swift music video with colorful visuals and artistic cinematography.",
            confidence_score=0.76
        )
        
        # Endgame - 2 descriptions
        endgame_desc1 = VideoDescription(
            video_id=endgame_video.id,
            description="Climactic action scene from Avengers: Endgame with superhero battle sequences.",
            confidence_score=0.94
        )
        endgame_desc2 = VideoDescription(
            video_id=endgame_video.id,
            description="Features dynamic camera angles with high angle shots and dramatic backlighting effects.",
            confidence_score=0.82
        )
        
        descriptions = [hp_desc, lotr_desc1, lotr_desc2, anime_desc, taylor_desc, endgame_desc1, endgame_desc2]
        db.session.add_all(descriptions)
        db.session.commit()
        
        print(f"Created {len(videos)} videos")
        print(f"Created {len(descriptions)} video descriptions")
        
        # Create VideoPropertyValue associations
        print("Creating VideoPropertyValue associations...")
        
        # Create associations between videos and property values
        # Each video gets at least 1 property, with a mix of different properties
        video_property_associations = [
            # Harry Potter video - magical/fantasy scene
            VideoPropertyValue(video_id=harry_potter_video.id, property_value_id=pan_left.id, confidence_score=1.0),
            VideoPropertyValue(video_id=harry_potter_video.id, property_value_id=angle_high.id, confidence_score=1.0),
            VideoPropertyValue(video_id=harry_potter_video.id, property_value_id=lighting_sidelight.id, confidence_score=1.0),
            
            # LOTR video - epic battle with tracking movement and sidelight
            VideoPropertyValue(video_id=lotr_video.id, property_value_id=camera_motion_forward.id, confidence_score=0.95),
            VideoPropertyValue(video_id=lotr_video.id, property_value_id=tracking_aerial.id, confidence_score=0.87),
            VideoPropertyValue(video_id=lotr_video.id, property_value_id=lighting_sidelight.id, confidence_score=0.79),
            
            # Anime video - dynamic action sequences
            VideoPropertyValue(video_id=anime_video.id, property_value_id=pan_right.id, confidence_score=0.82),
            VideoPropertyValue(video_id=anime_video.id, property_value_id=angle_low.id, confidence_score=0.76),
            VideoPropertyValue(video_id=anime_video.id, property_value_id=lighting_backlight.id, confidence_score=0.84),
            VideoPropertyValue(video_id=anime_video.id, property_value_id=tracking_lead.id, confidence_score=0.90),
            
            # Taylor Swift video - artistic cinematography
            VideoPropertyValue(video_id=taylor_swift_video.id, property_value_id=camera_motion_dolly_zoom.id, confidence_score=0.93),
            VideoPropertyValue(video_id=taylor_swift_video.id, property_value_id=lighting_underlight.id, confidence_score=0.71),
            
            # Endgame video - dynamic angles and backlighting
            VideoPropertyValue(video_id=endgame_video.id, property_value_id=angle_high.id, confidence_score=0.86),
            VideoPropertyValue(video_id=endgame_video.id, property_value_id=lighting_backlight.id, confidence_score=0.92),
            VideoPropertyValue(video_id=endgame_video.id, property_value_id=tracking_tail.id, confidence_score=0.77),
            VideoPropertyValue(video_id=endgame_video.id, property_value_id=camera_motion_backward.id, confidence_score=0.81),
        ]
        
        db.session.add_all(video_property_associations)
        db.session.commit()
        
        print(f"Created {len(video_property_associations)} video-property associations")
        
        # Create Users
        print("Creating Users...")
        
        # Create users with hashed passwords
        ryan1_user = User(
            username="ryan1",
            email="ryan1@gmail.com",
            password="password123"  # This will be automatically hashed by the password setter
        )
        
        ryan2_user = User(
            username="ryan2",
            email="ryan2@gmail.com",
            password="password123"  # This will be automatically hashed by the password setter
        )

        users = [ryan1_user, ryan2_user]
        db.session.add_all(users)
        db.session.commit()
        
        print(f"Created {len(users)} users")
        
        # Create Collections, UserCollection, and CollectionVideo
        print("Creating Collections and associations...")
        
        # Create collections
        action_collection = Collection(
            collection_name="Action",
            owner_id=ryan1_user.id
        )
        
        random_collection = Collection(
            collection_name="Random",
            owner_id=ryan2_user.id
        )
        
        collections = [action_collection, random_collection]
        db.session.add_all(collections)
        db.session.commit()  # Commit to get IDs for foreign keys
        
        # Create UserCollection for sharing (Action collection shared with ryan2_user)
        action_share = UserCollection(
            user_id=ryan2_user.id,
            collection_id=action_collection.id
        )
        
        user_collection_shares = [action_share]
        db.session.add_all(user_collection_shares)
        db.session.commit()
        
        # Create CollectionVideo associations
        # Action collection: superhero anime + endgame videos
        action_anime = CollectionVideo(
            collection_id=action_collection.id,
            video_id=anime_video.id  # superhero anime
        )
        
        action_endgame = CollectionVideo(
            collection_id=action_collection.id,
            video_id=endgame_video.id  # endgame
        )
        
        # Random collection: endgame + music video + LOTR videos
        random_endgame = CollectionVideo(
            collection_id=random_collection.id,
            video_id=endgame_video.id  # endgame
        )
        
        random_taylor = CollectionVideo(
            collection_id=random_collection.id,
            video_id=taylor_swift_video.id  # taylor swift music video
        )
        
        random_lotr = CollectionVideo(
            collection_id=random_collection.id,
            video_id=lotr_video.id  # LOTR
        )
        
        collection_videos = [action_anime, action_endgame, random_endgame, random_taylor, random_lotr]
        db.session.add_all(collection_videos)
        db.session.commit()
        
        print(f"Created {len(collections)} collections")
        print(f"Created {len(user_collection_shares)} collection shares")
        print(f"Created {len(collection_videos)} collection-video associations")
        
        print("Test data population completed!")

if __name__ == "__main__":
    populate_test_data()
