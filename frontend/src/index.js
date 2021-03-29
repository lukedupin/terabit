import React from 'react';
import ReactDOM from 'react-dom';
import Search from "./search";
import FilterBy from "./filter_by";
import Util from './util'
import distance from './geo'

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
        this.handleFilter = this.handleFilter.bind(this);

        this.timerId = -1
        this.update_view = false
        this.new_view = false
    }

    componentDidMount() {
        const { lng, lat, zoom } = this.state;
        this.map = new mapboxgl.Map({
            container: this.mapContainer.current,
            style: 'mapbox://styles/mapbox/streets-v11',
            center: [lng, lat],
            zoom: zoom
        });

        this.map.on('move', () => {
            this.setState( {
                lng: this.map.getCenter().lng,
                lat: this.map.getCenter().lat,
                zoom: this.map.getZoom()
            });
        });

        this.timerId = setInterval(this.updateView.bind(this), 350);
    }

    componentWillUnmount(){
        clearInterval(this.timerId);
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        this.new_view = true
        this.update_view = true
    }

    updateView() {
        //All of this ensure we don't double up on requests
        if ( !this.update_view ) {
            return
        }
        if ( this.new_view ) {
            this.new_view = false
            return
        }
        this.update_view = false

        //Run my view update
        const sw = this.map.getBounds()._sw;
        const { lat, lng, zoom } = this.state;
        const radius = distance( lat, lng, sw.lat, sw.lng );
        Util.fetch_js('/land/search_proximity/', { lat, lng, radius })
            .then( js => {
                Util.response(js, () => {
                    for ( let i = 0; i < js.lands.length; i++) {
                        console.log( js.lands[i].name )
                    }
                })
            })
    }

    handleFilter( js ) {
    }

    handleSearch( js ) {
        map.flyTo({
            center: [ js.lng, js.lat ],
            essential: true
        });

        this.setState({
            lat: js.lat,
            lng: js.lng,
        });
    }

    render() {
        //const { lng, lat, zoom } = this.state;
        return (
            <div>
                <Search />
                <FilterBy
                    onChange={this.handleFilter}
                />
                <div ref={this.mapContainer} className="map-container" />
            </div>
        );
    }
}

ReactDOM.render(<Map />, document.getElementById('app'));
