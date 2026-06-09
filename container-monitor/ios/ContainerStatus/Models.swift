import Foundation

/// Top-level response from `GET /api/containers`.
struct ContainersResponse: Codable {
    let hosts: [HostResult]
    let fetchedAt: String
}

/// Per-host result. `ok == false` means the agent could not reach that host;
/// `error` then explains why.
struct HostResult: Codable, Identifiable {
    var id: String { host }
    let host: String
    let ok: Bool
    let error: String?
    let containers: [Container]
}

/// A single container as reported by `docker ps`.
struct Container: Codable, Identifiable {
    var id: String { containerID }
    let containerID: String
    let name: String
    let image: String
    let state: String
    let status: String
    let ports: String
    let createdAt: String

    enum CodingKeys: String, CodingKey {
        case containerID = "id"
        case name, image, state, status, ports, createdAt
    }
}

extension Container {
    /// Maps Docker's `state` to a UI color bucket.
    var isRunning: Bool { state.lowercased() == "running" }
    var isStopped: Bool {
        let s = state.lowercased()
        return s == "exited" || s == "dead"
    }
}
