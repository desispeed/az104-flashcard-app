import Foundation
import Combine

@MainActor
final class ContainersViewModel: ObservableObject {
    @Published var hosts: [HostResult] = []
    @Published var fetchedAt: String?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private var timer: Timer?

    func load(settings: AppSettings) async {
        guard settings.isConfigured else {
            errorMessage = "Set the backend URL and API token in Settings."
            return
        }
        isLoading = true
        errorMessage = nil
        let client = APIClient(baseURL: settings.baseURL, token: settings.token)
        do {
            let response = try await client.fetchContainers()
            hosts = response.hosts
            fetchedAt = response.fetchedAt
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }

    /// Refresh every `interval` seconds while the view is visible.
    func startAutoRefresh(every interval: TimeInterval, settings: AppSettings) {
        stopAutoRefresh()
        timer = Timer.scheduledTimer(withTimeInterval: interval, repeats: true) { [weak self] _ in
            Task { await self?.load(settings: settings) }
        }
    }

    func stopAutoRefresh() {
        timer?.invalidate()
        timer = nil
    }
}
