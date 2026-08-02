#!/bin/sh
set -eu

start_dir=${1:-.}

if [ ! -d "$start_dir" ]; then
  printf 'error=directory_not_found\npath=%s\n' "$start_dir" >&2
  exit 2
fi

project_dir=$(cd "$start_dir" && pwd)
while [ "$project_dir" != "/" ] && [ ! -f "$project_dir/pubspec.yaml" ]; do
  project_dir=$(dirname "$project_dir")
done

if [ ! -f "$project_dir/pubspec.yaml" ]; then
  printf 'error=pubspec_not_found\nstart_path=%s\n' "$start_dir" >&2
  exit 3
fi

if command -v rg >/dev/null 2>&1; then
  match_file() {
    pattern=$1
    file=$2
    rg -q "$pattern" "$file" 2>/dev/null
  }
  match_tree() {
    pattern=$1
    shift
    rg -q "$pattern" "$@" 2>/dev/null
  }
else
  match_file() {
    pattern=$1
    file=$2
    grep -Eq "$pattern" "$file" 2>/dev/null
  }
  match_tree() {
    pattern=$1
    shift
    grep -ERq "$pattern" "$@" 2>/dev/null
  }
fi

yes_no() {
  if "$@"; then printf 'yes'; else printf 'no'; fi
}

pubspec="$project_dir/pubspec.yaml"
lockfile="$project_dir/pubspec.lock"
lib_dir="$project_dir/lib"

match_dependency() {
  pattern=$1
  match_file "$pattern" "$pubspec" || {
    [ -f "$lockfile" ] && match_file "$pattern" "$lockfile"
  }
}

flutter=$(yes_no match_file 'sdk:[[:space:]]*flutter|^[[:space:]]*flutter:' "$pubspec")
powersync=$(yes_no match_dependency '^[[:space:]]*powersync:')
drift=$(yes_no match_dependency '^[[:space:]]*drift:')
drift_dev=$(yes_no match_dependency '^[[:space:]]*drift_dev:')
drift_adapter=$(yes_no match_dependency '^[[:space:]]*drift_sqlite_async:')
sqlite_async=$(yes_no match_dependency '^[[:space:]]*sqlite_async:')
supabase=$(yes_no match_dependency '^[[:space:]]*supabase_flutter:')
firebase=$(yes_no match_dependency '^[[:space:]]*firebase_auth:')
workmanager=$(yes_no match_dependency '^[[:space:]]*workmanager:')
riverpod=$(yes_no match_dependency '^[[:space:]]*(flutter_riverpod|hooks_riverpod|riverpod):')

drift_code=no
powersync_code=no
adapter_code=no
if [ -d "$lib_dir" ]; then
  drift_code=$(yes_no match_tree "package:drift/drift\.dart|@DriftDatabase|extends[[:space:]]+GeneratedDatabase" "$lib_dir")
  powersync_code=$(yes_no match_tree "package:powersync/|PowerSyncDatabase|PowerSyncBackendConnector" "$lib_dir")
  adapter_code=$(yes_no match_tree "drift_sqlite_async|SqliteAsyncDriftConnection" "$lib_dir")
fi

config_dir=no
[ -d "$project_dir/powersync" ] && config_dir=yes

if [ "$drift_adapter" = yes ] || [ "$adapter_code" = yes ]; then
  recommendation=drift-adapter-present
elif [ "$drift" = yes ] || [ "$drift_code" = yes ]; then
  recommendation=drift-adapter
else
  recommendation=native-powersync
fi

printf 'project_root=%s\n' "$project_dir"
printf 'flutter=%s\n' "$flutter"
printf 'powersync_dependency=%s\n' "$powersync"
printf 'powersync_code=%s\n' "$powersync_code"
printf 'drift_dependency=%s\n' "$drift"
printf 'drift_dev_dependency=%s\n' "$drift_dev"
printf 'drift_code=%s\n' "$drift_code"
printf 'drift_sqlite_async_dependency=%s\n' "$drift_adapter"
printf 'drift_adapter_code=%s\n' "$adapter_code"
printf 'sqlite_async_dependency=%s\n' "$sqlite_async"
printf 'supabase_flutter=%s\n' "$supabase"
printf 'firebase_auth=%s\n' "$firebase"
printf 'workmanager=%s\n' "$workmanager"
printf 'riverpod=%s\n' "$riverpod"
printf 'powersync_config_directory=%s\n' "$config_dir"
printf 'recommended_client_path=%s\n' "$recommendation"

case "$recommendation" in
  drift-adapter)
    printf 'next_step=preserve_drift_and_add_drift_sqlite_async\n'
    ;;
  drift-adapter-present)
    printf 'next_step=inspect_existing_shared_connection_before_editing\n'
    ;;
  native-powersync)
    printf 'next_step=use_powersync_database_api_directly\n'
    ;;
esac
