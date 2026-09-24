## Search State

- **Seed**: 2
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → align → descend → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 11 | 0.1867 | 0.88 | ✅ accepted |
| 2 | align → approach → contact → insert → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 4 | -0.2343 | 0.00 | ❌ rejected |
| 1 | align → approach → contact → insert → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 4 | -0.2343 | 0.00 | ❌ rejected |
| 0 | align → approach → contact → insert → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 4 | -0.2343 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.88 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.882, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.187) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_hover
  offset:
  - 0.0
  - 0.0
  - 0.04
  weight: 0.2
- id: reach_entry
  weight: 0.3
- id: insertion_midpoint
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - -0.025
  weight: 0.5
phases:
- id: approach_above
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.04
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_z_offset:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_hover
- id: align_to_entry
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.01
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    lateral_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    lateral_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_entry
- id: descend_to_entry
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    descend_contact_force:
      type: scalar
      range:
      - 2.0
      - 12.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_entry
- id: insert_downward
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.04
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    insert_force_threshold:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 25.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
      binds_to:
      - path: generator.speed
        mode: replace
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: safety_force
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.002
    - 0.002
    - 0.0
  subtask_id: insertion_midpoint
- id: retract_upward
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.04], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
- **align_to_entry** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_x: status=consumed; consumers=target.offset.x (replace)
    - lateral_y: status=consumed; consumers=target.offset.y (replace)
- **descend_to_entry** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **insert_downward** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.04, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - insert_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=safety_force, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.002, 0.002, 0.0]
- **retract_upward** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.187
- **task_score** (E): 0.882
- **fitness_score**: 0.627  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 0.00 | 0.1795 |
| align_to_entry | 1.00 | 0.00 | 0.0329 |
| descend_to_entry | 0.00 | 0.00 | 0.0118 |
| insert_downward | 0.67 | 1.00 | 0.0308 |
| retract_upward | 1.00 | 0.00 | 0.0410 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.492, -0.007, 0.124) | (0.504, -0.000, 0.340)→(0.492, -0.007, 0.164) | 0.260→0.089 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_to_entry | align | 1.00 / step_budget | (0.492, -0.007, 0.124)→(0.494, -0.008, 0.091) | (0.492, -0.007, 0.164)→(0.495, -0.008, 0.131) | 0.089→0.057 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_entry | descend | 0.00 / step_budget | (0.494, -0.008, 0.091)→(0.493, -0.010, 0.081) | (0.495, -0.008, 0.131)→(0.494, -0.010, 0.121) | 0.057→0.051 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_downward | insert | 0.67 / force_exceeded | (0.493, -0.010, 0.081)→(0.490, -0.011, 0.051) | (0.494, -0.010, 0.121)→(0.492, -0.011, 0.090) | 0.051→0.034 | 1.00 / 1.000 | 61.947 | 21.626 |
| retract_upward | retract | 1.00 / step_budget | (0.471, -0.017, 0.051)→(0.467, -0.015, 0.091) | (0.472, -0.017, 0.090)→(0.469, -0.015, 0.131) | 0.034→0.062 | 0.00 / 0.000 | 0.000 | 54.226 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.911
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.911
- phase_score: 0.498
- phase_breakdown.reach_entry_score: 0.642
- phase_breakdown.insertion_midpoint_score: 0.363
- phase_breakdown.reach_hover_score: 0.622

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.663
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.911
- **Median Q (composite search score)**: 0.187
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at upper bound**: align_to_entry.lateral_x
- **Final σ (mean)**: 0.309


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.80769,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.align_speed":0.06063,"align_to_entry.lateral_x":0.01,"align_to_entry.lateral_y":0.00631,"approach_above.approach_speed":0.0813,"approach_above.approach_z_offset":0.03521,"descend_to_entry.descend_contact_force":6.95226,"descend_to_entry.descend_speed":0.02403,"insert_downward.insert_force_threshold":33.95786,"insert_downward.insert_speed":0.01509,"insert_downward.insertion_depth":0.05898,"retract_upward.retract_speed":0.0713},"optimized_scores":{"best_composite_score":0.22344,"best_fitness_score":0.66344,"best_task_score":0.91114},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.49258,-0.01428,0.04997],"force_p95":52.75831,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.85218,"mean_force":34.19863,"phase_index":4.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.4776,-0.014,0.05053]}],"total_contact_groups":1},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47423,-0.01238,0.09141],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":61.02105,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.47946,-0.0106,0.16311],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08627,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_hover","tcp_end":[0.47903,-0.01059,0.12311],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":305.0,"n_steps_budget":600.0,"object_pos_end":[0.48684,-0.00989,0.12946],"object_pos_start":[0.47946,-0.0106,0.16311],"object_to_goal_dist_end":0.05212,"object_to_goal_dist_start":0.08627,"object_z_max":0.16311,"peak_contact_force":0.0,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.48596,-0.00988,0.08946],"tcp_start":[0.47903,-0.01059,0.12311],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":47.0,"n_steps_budget":600.0,"object_pos_end":[0.48293,-0.01232,0.12303],"object_pos_start":[0.48684,-0.00989,0.12946],"object_to_goal_dist_end":0.04791,"object_to_goal_dist_start":0.05212,"object_z_max":0.12946,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.4818,-0.0123,0.08305],"tcp_start":[0.48596,-0.00988,0.08946],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.47926,-0.01403,0.09055],"object_pos_start":[0.48293,-0.01232,0.12303],"object_to_goal_dist_end":0.02717,"object_to_goal_dist_start":0.04791,"object_z_max":0.12303,"peak_contact_force":61.02105,"phase_name":"insert_downward","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_midpoint","tcp_end":[0.47769,-0.014,0.05058],"tcp_start":[0.4818,-0.0123,0.08305],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":370.0,"n_steps_budget":600.0,"object_pos_end":[0.47622,-0.01242,0.13136],"object_pos_start":[0.47926,-0.01403,0.09055],"object_to_goal_dist_end":0.05794,"object_to_goal_dist_start":0.02717,"object_z_max":0.13127,"peak_contact_force":0.0,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":6.0,"raw_peak_contact_force":54.85218,"tcp_end":[0.47423,-0.01238,0.09141],"tcp_start":[0.47769,-0.014,0.05058],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.7625,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.align_speed":0.0606,"align_to_entry.lateral_x":0.01,"align_to_entry.lateral_y":0.00436,"approach_above.approach_speed":0.06389,"approach_above.approach_z_offset":0.03662,"descend_to_entry.descend_contact_force":2.17153,"descend_to_entry.descend_speed":0.03483,"insert_downward.insert_force_threshold":20.768,"insert_downward.insert_speed":0.01958,"insert_downward.insertion_depth":0.0377,"retract_upward.retract_speed":0.06805},"optimized_scores":{"best_composite_score":0.14927,"best_fitness_score":0.58927,"best_task_score":0.84492},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.47838,-0.02054,0.04993],"force_p95":51.25212,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.5992,"mean_force":29.57111,"phase_index":4.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.4634,-0.02011,0.05044]}],"total_contact_groups":1},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46013,-0.01839,0.09121],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":59.94263,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":595.0,"n_steps_budget":1000.0,"object_pos_end":[0.4663,-0.0152,0.16435],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0921,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_hover","tcp_end":[0.46587,-0.01518,0.12436],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":283.0,"n_steps_budget":600.0,"object_pos_end":[0.47276,-0.01645,0.13044],"object_pos_start":[0.4663,-0.0152,0.16435],"object_to_goal_dist_end":0.05964,"object_to_goal_dist_start":0.0921,"object_z_max":0.16435,"peak_contact_force":0.0,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.4719,-0.01643,0.09044],"tcp_start":[0.46587,-0.01518,0.12436],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":46.0,"n_steps_budget":600.0,"object_pos_end":[0.46894,-0.0182,0.12385],"object_pos_start":[0.47276,-0.01645,0.13044],"object_to_goal_dist_end":0.05674,"object_to_goal_dist_start":0.05964,"object_z_max":0.13044,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.46783,-0.01817,0.08387],"tcp_start":[0.4719,-0.01643,0.09044],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.46503,-0.02017,0.09042],"object_pos_start":[0.46894,-0.0182,0.12385],"object_to_goal_dist_end":0.04169,"object_to_goal_dist_start":0.05674,"object_z_max":0.12385,"peak_contact_force":59.94263,"phase_name":"insert_downward","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_midpoint","tcp_end":[0.4635,-0.02012,0.05045],"tcp_start":[0.46783,-0.01817,0.08387],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":353.0,"n_steps_budget":600.0,"object_pos_end":[0.46208,-0.01845,0.13116],"object_pos_start":[0.46503,-0.02017,0.09042],"object_to_goal_dist_end":0.0663,"object_to_goal_dist_start":0.04169,"object_z_max":0.13107,"peak_contact_force":0.0,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":7.0,"raw_peak_contact_force":53.5992,"tcp_end":[0.46013,-0.01839,0.09121],"tcp_start":[0.4635,-0.02012,0.05045],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92188,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_entry.align_speed":0.03295,"align_to_entry.lateral_x":-0.01,"align_to_entry.lateral_y":0.00187,"approach_above.approach_speed":0.06394,"approach_above.approach_z_offset":0.03665,"descend_to_entry.descend_contact_force":7.47472,"descend_to_entry.descend_speed":0.01886,"insert_downward.insert_force_threshold":22.58244,"insert_downward.insert_speed":0.02456,"insert_downward.insertion_depth":0.03813,"retract_upward.retract_speed":0.04537},"optimized_scores":{"best_composite_score":0.18726,"best_fitness_score":0.62726,"best_task_score":0.88948},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.54434,0.00111,0.04998],"force_p95":64.87842,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.87842,"mean_force":64.87842,"phase_index":3.0,"phase_name":"insert_downward","phase_type":"insert","tcp_position_centroid":[0.52936,0.0009,0.05066]}],"total_contact_groups":1},"final_pose_error":0.01059,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.52938,0.0009,0.05056],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":64.87842,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.53018,0.00506,0.16344],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08888,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_hover","tcp_end":[0.5297,0.00506,0.12344],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":146.0,"n_steps_budget":660.0,"object_pos_end":[0.52402,0.00333,0.13433],"object_pos_start":[0.53018,0.00506,0.16344],"object_to_goal_dist_end":0.05949,"object_to_goal_dist_start":0.08888,"object_z_max":0.16344,"peak_contact_force":0.0,"phase_name":"align_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.52308,0.00332,0.09434],"tcp_start":[0.5297,0.00506,0.12344],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":430.0,"n_steps_budget":660.0,"object_pos_end":[0.53162,0.0011,0.1163],"object_pos_start":[0.52402,0.00333,0.13433],"object_to_goal_dist_end":0.04815,"object_to_goal_dist_start":0.05949,"object_z_max":0.13433,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.5302,0.00109,0.07632],"tcp_start":[0.52308,0.00332,0.09434],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":170.0,"n_steps_budget":900.0,"object_pos_end":[0.53126,0.00092,0.09051],"object_pos_start":[0.53162,0.0011,0.1163],"object_to_goal_dist_end":0.033,"object_to_goal_dist_start":0.04815,"object_z_max":0.1163,"peak_contact_force":64.87842,"phase_name":"insert_downward","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":64.87842,"subtask_id":"insertion_midpoint","tcp_end":[0.52938,0.0009,0.05056],"tcp_start":[0.5302,0.00109,0.07632],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```