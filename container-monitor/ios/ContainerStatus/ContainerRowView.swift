import SwiftUI

struct ContainerRowView: View {
    let container: Container

    private var statusColor: Color {
        if container.isRunning { return .green }
        if container.isStopped { return .red }
        return .yellow
    }

    var body: some View {
        HStack(spacing: 12) {
            Circle()
                .fill(statusColor)
                .frame(width: 10, height: 10)
            VStack(alignment: .leading, spacing: 2) {
                Text(container.name)
                    .font(.body)
                    .lineLimit(1)
                Text(container.image)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
                if !container.ports.isEmpty {
                    Text(container.ports)
                        .font(.caption2)
                        .foregroundStyle(.tertiary)
                        .lineLimit(1)
                }
            }
            Spacer()
            Text(container.status)
                .font(.caption2)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.trailing)
        }
        .padding(.vertical, 2)
    }
}
