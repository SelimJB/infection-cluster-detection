import pandas as pd
from io import StringIO
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import hashlib


@dataclass
class InfectionEpisode:
    """Represents an infection episode for a patient"""
    episode_id: str
    patient_id: str
    infection_type: str
    episode_number: int
    episode_start: date
    episode_end: date
    positive_tests: List[Dict]

    def get_infectious_window(self) -> Tuple[date, date]:
        """Get the infectious window for this episode"""
        return (self.episode_start, self.episode_end)

    def overlaps_with(self, other: 'InfectionEpisode') -> bool:
        """Check if this episode's window overlaps with another episode"""
        return not (self.episode_end < other.episode_start or
                    other.episode_end < self.episode_start)


@dataclass
class ContactEdge:
    """Represents a contact between two episodes"""
    episode_a: str
    episode_b: str
    contact_date: date
    location: str
    contact_type: str = "same_location_same_day"
    weight: float = 1.0


@dataclass
class EpisodeCluster:
    """Represents a cluster of connected infection episodes"""
    cluster_id: str
    infection_type: str
    episodes: List[InfectionEpisode]
    unique_patients: Set[str]
    locations: Set[str]
    date_range: Tuple[date, date]
    contact_events: List[ContactEdge]

    @property
    def patient_count(self) -> int:
        return len(self.unique_patients)

    @property
    def episode_count(self) -> int:
        return len(self.episodes)

    @property
    def duration_days(self) -> int:
        return (self.date_range[1] - self.date_range[0]).days

    @property
    def risk_score(self) -> float:
        """Risk score based on contact density"""
        return len(self.contact_events) / max(1, self.patient_count)

    def get_display_name(self) -> str:
        """User-friendly display name"""
        locations_str = ','.join(sorted(self.locations)[:3])
        if len(self.locations) > 3:
            locations_str += f" (+{len(self.locations)-3})"

        date_str = f"{self.date_range[0].strftime('%Y-%m-%d')} → {self.date_range[1].strftime('%Y-%m-%d')}"

        return f"{self.infection_type} — Wards {locations_str} — {date_str} — {self.patient_count} patients"

    def get_technical_id(self) -> str:
        """Technical ID for systems"""
        min_date_str = self.date_range[0].strftime('%Y-%m-%d')
        locations_hash = hashlib.md5(
            ''.join(sorted(self.locations)).encode()).hexdigest()[:4].upper()

        return f"cluster_{self.infection_type.lower()}_{min_date_str}_{locations_hash}"


class UnionFind:
    """Union-Find data structure for efficient cluster detection"""

    def __init__(self, elements):
        self.parent = {elem: elem for elem in elements}
        self.rank = {elem: 0 for elem in elements}

    def find(self, x):
        """Find root with path compression"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        """Union by rank"""
        root_x, root_y = self.find(x), self.find(y)

        if root_x != root_y:
            if self.rank[root_x] < self.rank[root_y]:
                root_x, root_y = root_y, root_x

            self.parent[root_y] = root_x
            if self.rank[root_x] == self.rank[root_y]:
                self.rank[root_x] += 1

    def get_components(self):
        """Get all connected components"""
        components = defaultdict(list)
        for elem in self.parent:
            root = self.find(elem)
            components[root].append(elem)
        return list(components.values())


def analyze_csv_data(csv_content_list):
    """
    Analyze CSV data using episode-based cluster detection

    Args:
        csv_content_list: List of dictionaries with 'filename' and 'content' keys

    Returns:
        dict: Analysis results with detected clusters
    """
    try:
        # Parse CSV files
        microbiology_data = None
        transfers_data = None

        for file_data in csv_content_list:
            filename = file_data.get("filename", "")
            content = file_data.get("content", "")

            if "microbiology" in filename.lower():
                microbiology_data = pd.read_csv(StringIO(content))
            elif "transfer" in filename.lower():
                transfers_data = pd.read_csv(StringIO(content))

        if microbiology_data is None or transfers_data is None:
            return {
                "error": "Both microbiology and transfers data required",
                "clusters": [],
                "episodes": [],
                "contacts": []
            }

        # Step 1: Prepare episodes
        episodes = prepare_episodes(microbiology_data)

        # Step 2: Build presence index
        presence_index = build_presence_index(episodes, transfers_data)

        # Step 3: Detect contacts
        contacts = detect_contacts(presence_index, episodes)

        # Step 4: Detect clusters by infection type
        all_clusters = []
        episodes_by_infection = group_episodes_by_infection(episodes)

        for infection_type, infection_episodes in episodes_by_infection.items():
            clusters = detect_clusters(
                infection_episodes, contacts, infection_type)
            all_clusters.extend(clusters)

        # Step 5: Format results
        results = {
            "total_episodes": len(episodes),
            "total_contacts": len(contacts),
            "total_clusters": len(all_clusters),
            "clusters_by_infection": {
                infection: len(
                    [c for c in all_clusters if c.infection_type == infection])
                for infection in episodes_by_infection.keys()
            },
            "clusters": [format_cluster_summary(cluster) for cluster in all_clusters],
            "episodes": [format_episode_summary(ep) for ep in episodes],
            "contacts": [format_contact_summary(contact) for contact in contacts],
            "summary_stats": calculate_summary_stats(all_clusters)
        }

        return results

    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "clusters": [],
            "episodes": [],
            "contacts": []
        }


def prepare_episodes(microbiology_data: pd.DataFrame) -> List[InfectionEpisode]:
    """
    Step 1: Prepare infection episodes from microbiology data
    """
    episodes = []

    # Filter positive tests
    positive_tests = microbiology_data[microbiology_data['result'] == 'positive'].copy(
    )

    if positive_tests.empty:
        return episodes

    # Convert date column
    positive_tests['collection_date'] = pd.to_datetime(
        positive_tests['collection_date']).dt.date

    # Group by (patient_id, infection)
    for (patient_id, infection), group in positive_tests.groupby(['patient_id', 'infection']):
        tests = group.sort_values('collection_date').to_dict('records')
        patient_episodes = create_episodes_for_patient(
            patient_id, infection, tests)
        episodes.extend(patient_episodes)

    return episodes


def create_episodes_for_patient(patient_id: str, infection: str, tests: List[Dict]) -> List[InfectionEpisode]:
    """
    Create episodes for a patient's infection, grouping tests that are close in time
    """
    episodes = []

    if not tests:
        return episodes

    # Group tests into episodes (tests within 28 days = same episode)
    episode_groups = []
    current_group = [tests[0]]

    for i in range(1, len(tests)):
        current_test = tests[i]
        last_test = current_group[-1]

        days_diff = (current_test['collection_date'] -
                     last_test['collection_date']).days

        if days_diff <= 28:  # Same episode
            current_group.append(current_test)
        else:  # New episode
            episode_groups.append(current_group)
            current_group = [current_test]

    episode_groups.append(current_group)

    # Create episode objects
    for episode_num, test_group in enumerate(episode_groups, 1):
        min_date = min(test['collection_date'] for test in test_group)
        max_date = max(test['collection_date'] for test in test_group)

        episode = InfectionEpisode(
            episode_id=f"{patient_id}_{infection}_EP{episode_num:03d}",
            patient_id=patient_id,
            infection_type=infection,
            episode_number=episode_num,
            episode_start=min_date - timedelta(days=14),
            episode_end=max_date + timedelta(days=14),
            positive_tests=test_group
        )
        episodes.append(episode)

    return episodes


def build_presence_index(episodes: List[InfectionEpisode], transfers_data: pd.DataFrame) -> Dict[Tuple[str, date], List[str]]:
    """
    Step 2: Build spatial-temporal presence index
    """
    presence_index = defaultdict(list)

    # Convert date column
    transfers_data = transfers_data.copy()
    transfers_data['date'] = pd.to_datetime(transfers_data['date']).dt.date

    for episode in episodes:
        # Find patient transfers during episode window
        patient_transfers = transfers_data[transfers_data['patient_id']
                                           == episode.patient_id]

        for _, transfer in patient_transfers.iterrows():
            transfer_date = transfer['date']

            # Check if transfer is within episode window
            if episode.episode_start <= transfer_date <= episode.episode_end:
                key = (transfer['location'], transfer_date)
                presence_index[key].append(episode.episode_id)

    return presence_index


def detect_contacts(presence_index: Dict[Tuple[str, date], List[str]], episodes: List[InfectionEpisode]) -> List[ContactEdge]:
    """
    Step 3: Detect contacts between episodes
    """
    contacts = []
    episodes_dict = {ep.episode_id: ep for ep in episodes}

    for (location, day), episode_ids in presence_index.items():
        if len(episode_ids) < 2:
            continue

        # Check all pairs of episodes present on this day
        for i in range(len(episode_ids)):
            for j in range(i + 1, len(episode_ids)):
                ep1_id, ep2_id = episode_ids[i], episode_ids[j]
                ep1, ep2 = episodes_dict[ep1_id], episodes_dict[ep2_id]

                # Same infection type and overlapping windows
                if (ep1.infection_type == ep2.infection_type and
                        ep1.overlaps_with(ep2)):

                    contact = ContactEdge(
                        episode_a=ep1_id,
                        episode_b=ep2_id,
                        contact_date=day,
                        location=location,
                        weight=1.0
                    )
                    contacts.append(contact)

    return contacts


def group_episodes_by_infection(episodes: List[InfectionEpisode]) -> Dict[str, List[InfectionEpisode]]:
    """
    Group episodes by infection type
    """
    episodes_by_infection = defaultdict(list)
    for episode in episodes:
        episodes_by_infection[episode.infection_type].append(episode)
    return episodes_by_infection


def detect_clusters(episodes: List[InfectionEpisode], contacts: List[ContactEdge], infection_type: str) -> List[EpisodeCluster]:
    """
    Step 4: Detect clusters using Union-Find
    """
    if len(episodes) < 2:
        return []

    # Filter contacts for this infection type
    relevant_contacts = [c for c in contacts
                         if any(ep.episode_id == c.episode_a and ep.infection_type == infection_type for ep in episodes)
                         and any(ep.episode_id == c.episode_b and ep.infection_type == infection_type for ep in episodes)]

    # Union-Find on episodes
    episode_ids = [ep.episode_id for ep in episodes]
    uf = UnionFind(episode_ids)

    for contact in relevant_contacts:
        uf.union(contact.episode_a, contact.episode_b)

    # Get connected components
    components = uf.get_components()

    # Create cluster objects
    clusters = []
    episodes_dict = {ep.episode_id: ep for ep in episodes}

    for component in components:
        if len(component) >= 2:  # At least 2 episodes for a cluster
            cluster_episodes = [episodes_dict[ep_id] for ep_id in component]
            cluster_contacts = [c for c in relevant_contacts
                                if c.episode_a in component and c.episode_b in component]

            cluster = create_cluster(
                infection_type, cluster_episodes, cluster_contacts)
            clusters.append(cluster)

    return clusters


def create_cluster(infection_type: str, episodes: List[InfectionEpisode], contacts: List[ContactEdge]) -> EpisodeCluster:
    """
    Create a cluster object from episodes and contacts
    """
    unique_patients = set(ep.patient_id for ep in episodes)
    locations = set()

    # Initialize with first episode dates
    min_date = episodes[0].episode_start
    max_date = episodes[0].episode_end

    for episode in episodes:
        if episode.episode_start < min_date:
            min_date = episode.episode_start
        if episode.episode_end > max_date:
            max_date = episode.episode_end

    for contact in contacts:
        locations.add(contact.location)

    cluster = EpisodeCluster(
        cluster_id="",  # Will be set by get_technical_id()
        infection_type=infection_type,
        episodes=episodes,
        unique_patients=unique_patients,
        locations=locations,
        date_range=(min_date, max_date),
        contact_events=contacts
    )

    cluster.cluster_id = cluster.get_technical_id()
    return cluster


def format_cluster_summary(cluster: EpisodeCluster) -> Dict:
    """
    Format cluster for results display
    """
    return {
        "cluster_id": cluster.cluster_id,
        "display_name": cluster.get_display_name(),
        "infection_type": cluster.infection_type,
        "patient_count": cluster.patient_count,
        "episode_count": cluster.episode_count,
        "locations": list(cluster.locations),
        "date_range": {
            "start": cluster.date_range[0].isoformat(),
            "end": cluster.date_range[1].isoformat()
        },
        "duration_days": cluster.duration_days,
        "risk_score": cluster.risk_score,
        "contacts_count": len(cluster.contact_events)
    }


def format_episode_summary(episode: InfectionEpisode) -> Dict:
    """
    Format episode for results display
    """
    return {
        "episode_id": episode.episode_id,
        "patient_id": episode.patient_id,
        "infection_type": episode.infection_type,
        "episode_number": episode.episode_number,
        "window": {
            "start": episode.episode_start.isoformat(),
            "end": episode.episode_end.isoformat()
        },
        "positive_tests_count": len(episode.positive_tests)
    }


def format_contact_summary(contact: ContactEdge) -> Dict:
    """
    Format contact for results display
    """
    return {
        "episode_a": contact.episode_a,
        "episode_b": contact.episode_b,
        "contact_date": contact.contact_date.isoformat(),
        "location": contact.location,
        "contact_type": contact.contact_type,
        "weight": contact.weight
    }


def calculate_summary_stats(clusters: List[EpisodeCluster]) -> Dict:
    """
    Calculate summary statistics
    """
    if not clusters:
        return {
            "total_patients_in_clusters": 0,
            "avg_cluster_size": 0,
            "largest_cluster_size": 0,
            "infections_with_clusters": []
        }

    all_patients = set()
    cluster_sizes = []
    infections = set()

    for cluster in clusters:
        all_patients.update(cluster.unique_patients)
        cluster_sizes.append(cluster.patient_count)
        infections.add(cluster.infection_type)

    return {
        "total_patients_in_clusters": len(all_patients),
        "avg_cluster_size": sum(cluster_sizes) / len(cluster_sizes),
        "largest_cluster_size": max(cluster_sizes),
        "infections_with_clusters": list(infections)
    }


def format_analysis_results(analysis_results):
    """
    Format analysis results for display
    """
    if "error" in analysis_results:
        return f"❌ Error: {analysis_results['error']}"

    output = []
    output.append("🧬 EPISODE-BASED CLUSTER DETECTION RESULTS")
    output.append("=" * 50)

    # Summary statistics
    output.append(f"📊 SUMMARY:")
    output.append(f"   • Total Episodes: {analysis_results['total_episodes']}")
    output.append(f"   • Total Contacts: {analysis_results['total_contacts']}")
    output.append(f"   • Total Clusters: {analysis_results['total_clusters']}")

    stats = analysis_results.get('summary_stats', {})
    if stats:
        output.append(
            f"   • Patients in Clusters: {stats['total_patients_in_clusters']}")
        output.append(
            f"   • Average Cluster Size: {stats['avg_cluster_size']:.1f} patients")
        output.append(
            f"   • Largest Cluster: {stats['largest_cluster_size']} patients")

    output.append("")

    # Clusters by infection type
    clusters_by_infection = analysis_results.get('clusters_by_infection', {})
    if clusters_by_infection:
        output.append("🦠 CLUSTERS BY INFECTION TYPE:")
        for infection, count in clusters_by_infection.items():
            output.append(f"   • {infection}: {count} clusters")
        output.append("")

    # Detailed cluster information
    clusters = analysis_results.get('clusters', [])
    if clusters:
        output.append("🔍 DETAILED CLUSTER INFORMATION:")
        output.append("")

        for i, cluster in enumerate(clusters, 1):
            output.append(f"Cluster {i}: {cluster['display_name']}")
            output.append(f"   ID: {cluster['cluster_id']}")
            output.append(f"   Episodes: {cluster['episode_count']}")
            output.append(f"   Duration: {cluster['duration_days']} days")
            output.append(f"   Risk Score: {cluster['risk_score']:.2f}")
            output.append(f"   Locations: {', '.join(cluster['locations'])}")
            output.append("")

    # Episodes summary
    episodes = analysis_results.get('episodes', [])
    if episodes:
        output.append(f"📋 EPISODES DETECTED: {len(episodes)}")
        infections = {}
        for ep in episodes:
            infection = ep['infection_type']
            infections[infection] = infections.get(infection, 0) + 1

        for infection, count in infections.items():
            output.append(f"   • {infection}: {count} episodes")
        output.append("")

    # Contacts summary
    contacts = analysis_results.get('contacts', [])
    if contacts:
        output.append(f"🤝 CONTACTS DETECTED: {len(contacts)}")
        locations = {}
        for contact in contacts:
            location = contact['location']
            locations[location] = locations.get(location, 0) + 1

        top_locations = sorted(
            locations.items(), key=lambda x: x[1], reverse=True)[:5]
        output.append("   Top contact locations:")
        for location, count in top_locations:
            output.append(f"     • {location}: {count} contacts")

    return "\n".join(output)
