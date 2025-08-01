from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from models import Stream, StreamOutput, StreamStats, StreamDestination
from stream_manager import stream_manager
from config import QUALITY_PROFILES, PLATFORM_ENDPOINTS
import logging

logger = logging.getLogger(__name__)

@app.route('/')
def dashboard():
    """Main dashboard showing all streams"""
    streams = Stream.query.order_by(Stream.created_at.desc()).all()
    return render_template('dashboard.html', streams=streams)

@app.route('/stream/new')
def new_stream():
    """Create new stream configuration"""
    destinations = StreamDestination.query.filter_by(enabled=True).all()
    return render_template('stream_config.html', 
                         stream=None, 
                         destinations=destinations,
                         quality_profiles=QUALITY_PROFILES,
                         platform_endpoints=PLATFORM_ENDPOINTS)

@app.route('/stream/<int:stream_id>/edit')
def edit_stream(stream_id):
    """Edit existing stream configuration"""
    stream = Stream.query.get_or_404(stream_id)
    destinations = StreamDestination.query.filter_by(enabled=True).all()
    return render_template('stream_config.html', 
                         stream=stream, 
                         destinations=destinations,
                         quality_profiles=QUALITY_PROFILES,
                         platform_endpoints=PLATFORM_ENDPOINTS)

@app.route('/stream/save', methods=['POST'])
def save_stream():
    """Save stream configuration"""
    try:
        stream_id = request.form.get('stream_id')
        name = request.form.get('name')
        input_url = request.form.get('input_url')
        input_type = request.form.get('input_type')
        latency_mode = request.form.get('latency_mode', 'low')
        record_enabled = request.form.get('record_enabled') == 'on'
        qualities = request.form.getlist('qualities')
        
        if stream_id:
            # Update existing stream
            stream = Stream.query.get(stream_id)
            if stream:
                stream.name = name
                stream.input_url = input_url
                stream.input_type = input_type
                stream.latency_mode = latency_mode
                stream.record_enabled = record_enabled
                db.session.commit()
                flash('Stream updated successfully', 'success')
        else:
            # Create new stream
            stream = stream_manager.create_stream(
                name=name,
                input_url=input_url,
                input_type=input_type,
                latency_mode=latency_mode,
                record_enabled=record_enabled,
                qualities=qualities
            )
            if stream:
                flash('Stream created successfully', 'success')
            else:
                flash('Error creating stream', 'error')
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Error saving stream: {e}")
        flash('Error saving stream configuration', 'error')
        return redirect(url_for('dashboard'))

@app.route('/stream/<int:stream_id>/start', methods=['POST'])
def start_stream(stream_id):
    """Start a stream"""
    try:
        success = stream_manager.start_stream(stream_id)
        if success:
            return jsonify({'status': 'success', 'message': 'Stream started'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to start stream'})
    except Exception as e:
        logger.error(f"Error starting stream {stream_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stream/<int:stream_id>/stop', methods=['POST'])
def stop_stream(stream_id):
    """Stop a stream"""
    try:
        success = stream_manager.stop_stream(stream_id)
        if success:
            return jsonify({'status': 'success', 'message': 'Stream stopped'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to stop stream'})
    except Exception as e:
        logger.error(f"Error stopping stream {stream_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stream/<int:stream_id>/status')
def stream_status(stream_id):
    """Get stream status"""
    try:
        stream = Stream.query.get_or_404(stream_id)
        from ffmpeg_service import ffmpeg_service
        ffmpeg_status = ffmpeg_service.get_stream_status(stream_id)
        
        return jsonify({
            'id': stream.id,
            'name': stream.name,
            'status': stream.status,
            'ffmpeg_status': ffmpeg_status,
            'updated_at': stream.updated_at.isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting stream status {stream_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stream/<int:stream_id>/stats')
def stream_stats(stream_id):
    """Get stream statistics"""
    try:
        stats = stream_manager.get_stream_stats(stream_id)
        return jsonify({'stats': stats})
    except Exception as e:
        logger.error(f"Error getting stream stats {stream_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stream/<int:stream_id>/destinations', methods=['POST'])
def update_destinations(stream_id):
    """Update stream destinations"""
    try:
        data = request.get_json() or {}
        destinations = data.get('destinations', [])
        success = stream_manager.update_stream_destinations(stream_id, destinations)
        
        if success:
            return jsonify({'status': 'success', 'message': 'Destinations updated'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to update destinations'})
    except Exception as e:
        logger.error(f"Error updating destinations for stream {stream_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stream/<int:stream_id>/player')
def stream_player(stream_id):
    """Stream player page"""
    embed_info = stream_manager.get_embed_info(stream_id)
    if not embed_info:
        flash('Stream not found', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('player.html', embed_info=embed_info)

@app.route('/stream/<int:stream_id>/embed')
def stream_embed(stream_id):
    """Embeddable stream player"""
    embed_info = stream_manager.get_embed_info(stream_id)
    if not embed_info:
        return "Stream not found", 404
    
    return render_template('embed.html', embed_info=embed_info)

@app.route('/destinations')
def destinations():
    """Manage stream destinations"""
    destinations = StreamDestination.query.all()
    return render_template('destinations.html', 
                         destinations=destinations,
                         platform_endpoints=PLATFORM_ENDPOINTS)

@app.route('/destination/save', methods=['POST'])
def save_destination():
    """Save stream destination"""
    try:
        name = request.form.get('name')
        platform = request.form.get('platform')
        rtmp_url = request.form.get('rtmp_url')
        stream_key = request.form.get('stream_key')
        
        if platform in PLATFORM_ENDPOINTS:
            rtmp_url = PLATFORM_ENDPOINTS[platform]
        
        destination = StreamDestination(
            name=name,
            platform=platform,
            rtmp_url=rtmp_url,
            stream_key=stream_key
        )
        
        db.session.add(destination)
        db.session.commit()
        
        flash('Destination saved successfully', 'success')
        return redirect(url_for('destinations'))
        
    except Exception as e:
        logger.error(f"Error saving destination: {e}")
        flash('Error saving destination', 'error')
        return redirect(url_for('destinations'))

@app.route('/destination/<int:dest_id>/delete', methods=['POST'])
def delete_destination(dest_id):
    """Delete stream destination"""
    try:
        destination = StreamDestination.query.get_or_404(dest_id)
        db.session.delete(destination)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Destination deleted'})
    except Exception as e:
        logger.error(f"Error deleting destination {dest_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/rtmp/status')
def rtmp_status():
    """Get RTMP server status"""
    try:
        from rtmp_server import rtmp_server
        status = rtmp_server.get_server_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting RTMP status: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/rtmp/start', methods=['POST'])
def start_rtmp_server():
    """Start RTMP server"""
    try:
        from rtmp_server import rtmp_server
        success = rtmp_server.start_server()
        if success:
            return jsonify({'status': 'success', 'message': 'RTMP server started'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to start RTMP server'})
    except Exception as e:
        logger.error(f"Error starting RTMP server: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/rtmp/stop', methods=['POST'])
def stop_rtmp_server():
    """Stop RTMP server"""
    try:
        from rtmp_server import rtmp_server
        success = rtmp_server.stop_server()
        if success:
            return jsonify({'status': 'success', 'message': 'RTMP server stopped'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to stop RTMP server'})
    except Exception as e:
        logger.error(f"Error stopping RTMP server: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

# RTMP webhook endpoints (for nginx-rtmp-module integration)
@app.route('/rtmp/publish', methods=['POST'])
def rtmp_publish():
    """Handle RTMP stream publish event"""
    try:
        from rtmp_server import rtmp_server
        
        # Get stream key from request
        stream_key = request.form.get('name') or request.form.get('key')
        client_ip = request.form.get('addr') or request.remote_addr
        
        if not stream_key:
            return jsonify({'status': 'error', 'message': 'No stream key provided'}), 400
        
        stream_id = rtmp_server.handle_stream_publish(stream_key, client_ip)
        
        if stream_id:
            return jsonify({'status': 'success', 'stream_id': stream_id})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to handle stream'}), 500
            
    except Exception as e:
        logger.error(f"Error handling RTMP publish: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/rtmp/unpublish', methods=['POST'])
def rtmp_unpublish():
    """Handle RTMP stream unpublish event"""
    try:
        from rtmp_server import rtmp_server
        
        stream_key = request.form.get('name') or request.form.get('key')
        
        if not stream_key:
            return jsonify({'status': 'error', 'message': 'No stream key provided'}), 400
        
        rtmp_server.handle_stream_unpublish(stream_key)
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error handling RTMP unpublish: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Documentation routes
@app.route('/docs')
@app.route('/docs/')
def docs_index():
    """Documentation index page"""
    return render_template('docs_index.html')

@app.route('/docs/tutorial')
def docs_tutorial():
    """Serve tutorial documentation"""
    try:
        with open('docs/TUTORIAL.md', 'r', encoding='utf-8') as f:
            content = f.read()
        return render_template('docs_page.html', 
                             title='Complete Tutorial', 
                             content=content,
                             doc_type='tutorial')
    except FileNotFoundError:
        return "Tutorial documentation not found", 404

@app.route('/docs/api')
def docs_api():
    """Serve API documentation"""
    try:
        with open('docs/API.md', 'r', encoding='utf-8') as f:
            content = f.read()
        return render_template('docs_page.html', 
                             title='API Documentation', 
                             content=content,
                             doc_type='api')
    except FileNotFoundError:
        return "API documentation not found", 404

@app.route('/docs/deployment')
def docs_deployment():
    """Serve deployment guide"""
    try:
        with open('docs/DEPLOYMENT.md', 'r', encoding='utf-8') as f:
            content = f.read()
        return render_template('docs_page.html', 
                             title='Deployment Guide', 
                             content=content,
                             doc_type='deployment')
    except FileNotFoundError:
        return "Deployment documentation not found", 404

@app.route('/docs/contributing')
def docs_contributing():
    """Serve contributing guide"""
    try:
        with open('docs/CONTRIBUTING.md', 'r', encoding='utf-8') as f:
            content = f.read()
        return render_template('docs_page.html', 
                             title='Contributing Guide', 
                             content=content,
                             doc_type='contributing')
    except FileNotFoundError:
        return "Contributing guide not found", 404
