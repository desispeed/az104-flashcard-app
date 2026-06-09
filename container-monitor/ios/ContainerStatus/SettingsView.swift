import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var settings: AppSettings
    @Environment(\.dismiss) private var dismiss

    @State private var baseURL = ""
    @State private var token = ""

    var body: some View {
        NavigationStack {
            Form {
                Section("Backend") {
                    TextField("https://your-agent:8080", text: $baseURL)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .keyboardType(.URL)
                    SecureField("API token", text: $token)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                }
                Section {
                    Text("The token is stored in the iOS Keychain and sent as a Bearer header. The agent reaches each host over SSH Docker contexts.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Settings")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        settings.baseURL = baseURL.trimmingCharacters(in: .whitespaces)
                        settings.token = token.trimmingCharacters(in: .whitespaces)
                        dismiss()
                    }
                }
            }
            .onAppear {
                baseURL = settings.baseURL
                token = settings.token
            }
        }
    }
}
