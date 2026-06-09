import Foundation
import Combine

/// Holds the backend connection settings. Base URL persists in UserDefaults;
/// the API token persists in the Keychain.
@MainActor
final class AppSettings: ObservableObject {
    private static let baseURLKey = "baseURL"
    private static let tokenKeychainKey = "com.containerstatus.apiToken"

    @Published var baseURL: String {
        didSet { UserDefaults.standard.set(baseURL, forKey: Self.baseURLKey) }
    }

    @Published var token: String {
        didSet {
            if token.isEmpty {
                Keychain.delete(Self.tokenKeychainKey)
            } else {
                Keychain.set(token, for: Self.tokenKeychainKey)
            }
        }
    }

    init() {
        self.baseURL = UserDefaults.standard.string(forKey: Self.baseURLKey) ?? ""
        self.token = Keychain.get(Self.tokenKeychainKey) ?? ""
    }

    var isConfigured: Bool {
        !baseURL.trimmingCharacters(in: .whitespaces).isEmpty
            && !token.trimmingCharacters(in: .whitespaces).isEmpty
    }
}
