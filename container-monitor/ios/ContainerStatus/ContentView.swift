import SwiftUI

struct ContentView: View {
    @EnvironmentObject var settings: AppSettings
    @StateObject private var viewModel = ContainersViewModel()
    @State private var showingSettings = false

    var body: some View {
        NavigationStack {
            Group {
                if !settings.isConfigured {
                    unconfiguredView
                } else {
                    containerList
                }
            }
            .navigationTitle("Containers")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        showingSettings = true
                    } label: {
                        Image(systemName: "gearshape")
                    }
                }
            }
            .sheet(isPresented: $showingSettings) {
                SettingsView()
            }
            .task {
                await viewModel.load(settings: settings)
                viewModel.startAutoRefresh(every: 15, settings: settings)
            }
            .onDisappear { viewModel.stopAutoRefresh() }
            .refreshable { await viewModel.load(settings: settings) }
        }
    }

    private var unconfiguredView: some View {
        ContentUnavailableView {
            Label("Not configured", systemImage: "server.rack")
        } description: {
            Text("Add your backend URL and API token to start monitoring.")
        } actions: {
            Button("Open Settings") { showingSettings = true }
                .buttonStyle(.borderedProminent)
        }
    }

    private var containerList: some View {
        List {
            if let error = viewModel.errorMessage {
                Section {
                    Label(error, systemImage: "exclamationmark.triangle")
                        .foregroundStyle(.red)
                }
            }
            ForEach(viewModel.hosts) { host in
                Section {
                    if !host.ok {
                        Label(host.error ?? "Unreachable", systemImage: "wifi.exclamationmark")
                            .foregroundStyle(.orange)
                            .font(.footnote)
                    } else if host.containers.isEmpty {
                        Text("No containers")
                            .foregroundStyle(.secondary)
                            .font(.footnote)
                    } else {
                        ForEach(host.containers) { container in
                            ContainerRowView(container: container)
                        }
                    }
                } header: {
                    HStack {
                        Text(host.host)
                        Spacer()
                        if host.ok {
                            Text("\(host.containers.filter { $0.isRunning }.count)/\(host.containers.count) up")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
            }
        }
        .overlay {
            if viewModel.isLoading && viewModel.hosts.isEmpty {
                ProgressView()
            }
        }
        .safeAreaInset(edge: .bottom) {
            if let fetchedAt = viewModel.fetchedAt {
                Text("Updated \(fetchedAt)")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .padding(.bottom, 4)
            }
        }
    }
}
