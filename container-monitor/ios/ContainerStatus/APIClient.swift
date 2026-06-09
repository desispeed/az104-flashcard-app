import Foundation

enum APIError: LocalizedError {
    case badURL
    case unauthorized
    case server(Int)
    case decoding(String)

    var errorDescription: String? {
        switch self {
        case .badURL: return "Invalid backend URL."
        case .unauthorized: return "Unauthorized — check your API token."
        case .server(let code): return "Server returned HTTP \(code)."
        case .decoding(let msg): return "Could not read response: \(msg)"
        }
    }
}

struct APIClient {
    let baseURL: String
    let token: String

    func fetchContainers() async throws -> ContainersResponse {
        let trimmed = baseURL.trimmingCharacters(in: .whitespaces)
            .trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        guard let url = URL(string: "\(trimmed)/api/containers") else {
            throw APIError.badURL
        }

        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.timeoutInterval = 30

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw APIError.server(-1)
        }
        if http.statusCode == 401 { throw APIError.unauthorized }
        guard (200..<300).contains(http.statusCode) else {
            throw APIError.server(http.statusCode)
        }

        do {
            return try JSONDecoder().decode(ContainersResponse.self, from: data)
        } catch {
            throw APIError.decoding(error.localizedDescription)
        }
    }
}
