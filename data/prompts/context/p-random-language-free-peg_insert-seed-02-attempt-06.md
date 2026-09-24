## Search State

- **Seed**: 2
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 10 | 0.4709 | 0.85 | ❌ rejected |
| 5 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | 0.5712 | 0.85 | ✅ accepted |
| 4 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.0712 | 0.10 | ❌ rejected |
| 3 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.0712 | 0.10 | ❌ rejected |
| 2 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.0712 | 0.10 | ❌ rejected |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_insert
- Frozen realised-scene SHA-256: `000fdf10fe8eedab7d155674d723f89be0845ff9d65630ae92397c5d3d89cf9a`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.48092897073994534, -0.016120708526870135, 0.08]
- Frozen socket pose: [0.48092897073994534, -0.016120708526870135, 0.025] (static fixture for this episode)
- Goal object position: (0.48092897073994534, -0.016120708526870135, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.4809, -0.0161, 0.08]
  frozen_socket_position: [0.4809, -0.0161, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.48092897073994534, -0.016120708526870135, 0.08]}
  frozen_fixtures: {'peg_socket': [0.48092897073994534, -0.016120708526870135, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 000fdf10fe8eedab7d155674d723f89be0845ff9d65630ae92397c5d3d89cf9a

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.848, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48092897073994534, -0.016120708526870135, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.48092897073994534, -0.016120708526870135, 0.025) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.471) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_entry
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.055
  weight: 0.3
- id: insertion_depth
  anchor: fixture
  metric: goal_progress
  weight: 0.7
phases:
- id: align_approach
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_entry
- id: descend_to_entry
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_height:
      type: scalar
      range:
      - 0.04
      - 0.07
      default: 0.055
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_entry
- id: insert_into_hole
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    offset_along_axis:
      distance: 0.055
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    insertion_depth_param:
      type: scalar
      range:
      - 0.04
      - 0.07
      default: 0.055
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_force:
      type: scalar
      range:
      - 10.0
      - 30.0
      default: 20
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insertion_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    retry_offset_x_param:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: -0.005
      binds_to:
      - path: retry.offset.x
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 35.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - -0.005
    - 0.0
    - 0.0
  subtask_id: insertion_depth

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_approach** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_entry** (`descend`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_height: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], offset_along_axis={axis=channel_axis, distance=0.055, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - insertion_depth_param: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_force: status=consumed; consumers=termination.force_threshold (replace)
    - insertion_speed: status=consumed; consumers=generator.speed (replace)
    - retry_offset_x_param: status=consumed; consumers=retry.offset.x (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=35.0
  - retries: max_attempts=2, strategy=offset_target, offset=[-0.005, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.471
- **task_score** (E): 0.847
- **fitness_score**: 0.668  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_approach | 1.00 | 0.00 | 0.1291 |
| descend_to_entry | 1.00 | 0.00 | 0.0714 |
| insert_into_hole | 1.00 | 1.00 | 0.0536 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, -0.011, 0.175) | (0.504, -0.000, 0.340)→(0.493, -0.011, 0.215) | 0.260→0.139 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_entry | descend | 1.00 / step_budget | (0.493, -0.011, 0.175)→(0.491, -0.012, 0.104) | (0.493, -0.011, 0.215)→(0.491, -0.012, 0.144) | 0.139→0.072 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_into_hole | insert | 1.00 / force_exceeded | (0.491, -0.012, 0.104)→(0.489, -0.012, 0.050) | (0.491, -0.012, 0.144)→(0.490, -0.012, 0.090) | 0.072→0.035 | 1.00 / 1.000 | 63.720 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.866
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.866
- phase_score: 0.586
- phase_breakdown.insertion_depth_score: 0.574
- phase_breakdown.approach_entry_score: 0.614

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.698
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.875
- **Median Q (composite search score)**: 0.496
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.417


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0683575c8c1f9a2e853486e53a70f2778dc5f31a7e19c0cc73869aa6c9b2eb38`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a66c77ff869939bbf3f6512e357ac544306e510caf9afe4ba80bb30952eb91b8`; realized-scene SHA-256: `000fdf10fe8eedab7d155674d723f89be0845ff9d65630ae92397c5d3d89cf9a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48093,-0.01612,0.025]},{"name":"target","value":[0.48093,-0.01612,0.025]},{"name":"socket","value":[0.48093,-0.01612,0.025]},{"name":"goal","value":[0.48093,-0.01612,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,-0.01612,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48093,-0.01612,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.41921,"average_solve_count":229.0,"average_success_count":229.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_approach.approach_height":0.16109,"align_approach.speed":0.04163,"descend_to_entry.descend_height":0.06981,"descend_to_entry.descend_speed":0.02585,"insert_into_hole.guard_force_threshold":17.79944,"insert_into_hole.insertion_depth_param":0.05132,"insert_into_hole.insertion_force":39.27021,"insert_into_hole.insertion_speed":0.00358,"insert_into_hole.retry_offset_x_param":-0.00171,"insert_into_hole.retry_offset_y_param":0.00694},"optimized_scores":{"best_composite_score":0.50142,"best_fitness_score":0.69809,"best_task_score":0.86599},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.02225,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47605,-0.01595,0.05039],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":63.36475,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.48101,-0.01407,0.23569],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15748,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_entry","tcp_end":[0.48056,-0.01407,0.1957],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.47847,-0.01579,0.14418],"object_pos_start":[0.48101,-0.01407,0.23569],"object_to_goal_dist_end":0.06951,"object_to_goal_dist_start":0.15748,"object_z_max":0.23569,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_entry","tcp_end":[0.47759,-0.01578,0.10419],"tcp_start":[0.48056,-0.01407,0.1957],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.47736,-0.01597,0.09037],"object_pos_start":[0.47847,-0.01579,0.14418],"object_to_goal_dist_end":0.02959,"object_to_goal_dist_start":0.06951,"object_z_max":0.14418,"peak_contact_force":63.36475,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_depth","tcp_end":[0.47605,-0.01595,0.05039],"tcp_start":[0.47759,-0.01578,0.10419],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f7a78497e90daffbc1f80091d8bb137dfe03b451997b9d2547738446c3b5abf7`; realized-scene SHA-256: `3a9889f49656bcc88af2945ad0b69da740661b3d51c4f32509721809854ac75e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.46685,-0.02106,0.025]},{"name":"target","value":[0.46685,-0.02106,0.025]},{"name":"socket","value":[0.46685,-0.02106,0.025]},{"name":"goal","value":[0.46685,-0.02106,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.02106,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.62275,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_approach.approach_height":0.16179,"align_approach.speed":0.07555,"descend_to_entry.descend_height":0.06998,"descend_to_entry.descend_speed":0.04938,"insert_into_hole.guard_force_threshold":14.65942,"insert_into_hole.insertion_depth_param":0.0502,"insert_into_hole.insertion_force":31.99953,"insert_into_hole.insertion_speed":0.00408,"insert_into_hole.retry_offset_x_param":-0.00998,"insert_into_hole.retry_offset_y_param":0.00333},"optimized_scores":{"best_composite_score":0.41519,"best_fitness_score":0.61186,"best_task_score":0.80064},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.02113,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46217,-0.02081,0.0504],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":60.92043,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":339.0,"n_steps_budget":990.0,"object_pos_end":[0.46864,-0.01846,0.23608],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.16027,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_entry","tcp_end":[0.46821,-0.01844,0.19609],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.46458,-0.02063,0.14426],"object_pos_start":[0.46864,-0.01846,0.23608],"object_to_goal_dist_end":0.07622,"object_to_goal_dist_start":0.16027,"object_z_max":0.23608,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_entry","tcp_end":[0.4637,-0.0206,0.10427],"tcp_start":[0.46821,-0.01844,0.19609],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.46347,-0.02085,0.09038],"object_pos_start":[0.46458,-0.02063,0.14426],"object_to_goal_dist_end":0.04332,"object_to_goal_dist_start":0.07622,"object_z_max":0.14426,"peak_contact_force":60.92043,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_depth","tcp_end":[0.46217,-0.02081,0.0504],"tcp_start":[0.4637,-0.0206,0.10427],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `874fa9670847c5f27a6a92c3fdc675c377c2cfbcb527691cf7211f9dd6015fe4`; realized-scene SHA-256: `03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53544,0.00091,0.025]},{"name":"target","value":[0.53544,0.00091,0.025]},{"name":"socket","value":[0.53544,0.00091,0.025]},{"name":"goal","value":[0.53544,0.00091,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.00091,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.57767,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_approach.approach_height":0.10097,"align_approach.speed":0.02588,"descend_to_entry.descend_height":0.06986,"descend_to_entry.descend_speed":0.05581,"insert_into_hole.guard_force_threshold":20.11193,"insert_into_hole.insertion_depth_param":0.07865,"insert_into_hole.insertion_force":31.97588,"insert_into_hole.insertion_speed":0.00959,"insert_into_hole.retry_offset_x_param":0.00047,"insert_into_hole.retry_offset_y_param":0.00114},"optimized_scores":{"best_composite_score":0.49596,"best_fitness_score":0.69263,"best_task_score":0.87499},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.04956,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.52861,0.00078,0.05044],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":66.87466,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":614.0,"n_steps_budget":1000.0,"object_pos_end":[0.52994,0.00079,0.17392],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09858,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_entry","tcp_end":[0.52946,0.00079,0.13393],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":108.0,"n_steps_budget":600.0,"object_pos_end":[0.53117,0.00082,0.14334],"object_pos_start":[0.52994,0.00079,0.17392],"object_to_goal_dist_end":0.0706,"object_to_goal_dist_start":0.09858,"object_z_max":0.17392,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_entry","tcp_end":[0.53027,0.00081,0.10335],"tcp_start":[0.52946,0.00079,0.13393],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.52999,0.00079,0.09041],"object_pos_start":[0.53117,0.00082,0.14334],"object_to_goal_dist_end":0.03176,"object_to_goal_dist_start":0.0706,"object_z_max":0.14334,"peak_contact_force":66.87466,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_depth","tcp_end":[0.52861,0.00078,0.05044],"tcp_start":[0.53027,0.00081,0.10335],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```