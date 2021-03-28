import React from 'react';
import ReactDOM from 'react-dom';

import mapboxgl from 'mapbox-gl/dist/mapbox-gl-unminified.js';
import MapboxWorker from 'worker-loader!mapbox-gl/dist/mapbox-gl-csp-worker';

mapboxgl.workerClass = MapboxWorker;
mapboxgl.accessToken = 'pk.eyJ1IjoidGVyYWJpdCIsImEiOiJja21zMnpkaXMwZGdqMm5teDdpNWN1ZHVkIn0.mIPDv8iZ1mMEq51n6jt10g';

function fetch_js( url, js ) {
    const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify( js )
    };

    return fetch( url, requestOptions )
}


class Map extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            lng: -70.9,
            lat: 42.35,
            zoom: 9
        };
        this.mapContainer = React.createRef();
    }

    componentDidMount() {
        const { lng, lat, zoom } = this.state;
        const map = new mapboxgl.Map({
            container: this.mapContainer.current,
            style: 'mapbox://styles/mapbox/streets-v11',
            center: [lng, lat],
            zoom: zoom
        });

        map.on('move', () => {
            this.setState({
                lng: map.getCenter().lng.toFixed(4),
                lat: map.getCenter().lat.toFixed(4),
                zoom: map.getZoom().toFixed(2)
            });
        });
    }

    onHandleSubmit() {
        fetch_js('/version/current/', { dog: 'A dog dog'} )
            .then( resp => resp.json())
            .then( res => console.log(res) );
    }

    render() {
        const { lng, lat, zoom } = this.state;
        return (
            <div>
                <div className="sidebar">
                    Longitude: {lng} | Latitude: {lat} | Zoom: {zoom}
                <button type="submit" onClick={this.onHandleSubmit}>Post a thing</button>
                </div>
                <div ref={this.mapContainer} className="map-container" />
            </div>
        );
    }
}

ReactDOM.render(<Map />, document.getElementById('app'));
