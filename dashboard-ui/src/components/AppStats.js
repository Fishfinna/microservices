import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

    const getStats = () => {

        fetch(`http://20.151.78.202:8100/stats`)
            .then(res => res.json())
            .then((result) => {
                console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            }, (error) => {
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
        const interval = setInterval(() => getStats(), 2000);
        return () => clearInterval(interval);
    }, [getStats]);

    if (error) {
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false) {
        return (<div>Loading...</div>)
    } else if (isLoaded === true) {
        return (
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
                    <tbody>
                        <tr>
                            <th>Blood Pressure</th>
                            <th>Heart Rate</th>
                        </tr>
                        <tr>
                            <td># Direction: {stats['num_direction_readings']}</td>
                            <td># Scale: {stats['num_scale_readings']}</td>
                        </tr>
                        <tr>
                            <td colspan="2">Max Direction Reading: {stats['max_direction_readings']}</td>
                        </tr>
                        <tr>
                            <td colspan="2">Max Scale Reading: {stats['max_scale_readings']}</td>
                        </tr>
                    </tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>
            </div>
        )
    }
}
