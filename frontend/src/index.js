import React from 'react';
import ReactDOM from 'react-dom';
import Search from "./search";
import FilterBy from "./filter_by";
import fetch_js from './util'

import mapboxgl from 'mapbox-gl/dist/mapbox-gl-unminified.js';
import MapboxWorker from 'worker-loader!mapbox-gl/dist/mapbox-gl-csp-worker';

mapboxgl.workerClass = MapboxWorker;
mapboxgl.accessToken = 'pk.eyJ1IjoidGVyYWJpdCIsImEiOiJja21zMnpkaXMwZGdqMm5teDdpNWN1ZHVkIn0.mIPDv8iZ1mMEq51n6jt10g';

class Map extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            lat: 37.7749,
            lng: -122.4194,
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
            const state = {
                lng: map.getCenter().lng.toFixed(4),
                lat: map.getCenter().lat.toFixed(4),
                zoom: map.getZoom().toFixed(2)
            }
            this.setState( state );

            console.log("Fetch for: "+ state.lat +", "+ state.lng);
        });
    }

    render() {
        //const { lng, lat, zoom } = this.state;
        return (
            <div>
                <Search />
                <FilterBy />
                <div ref={this.mapContainer} className="map-container" />
            </div>
        );
    }
}

ReactDOM.render(<Map />, document.getElementById('app'));
