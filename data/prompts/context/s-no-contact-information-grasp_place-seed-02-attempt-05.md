## Search State

- **Seed**: 2
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | -0.1063 | 0.27 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | -0.0186 | 0.16 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | -0.1681 | 0.16 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | -0.1022 | 0.16 | ✅ accepted |
| 1 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

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
| `object` | offset from object initial position (0.4761612134249316, -0.02015088565858767, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=-0.106) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_object
  anchor: object
  target_entity: object
  metric: contact
  weight: 0.3
- id: lift_clearance
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_at_goal
  target_entity: object
  weight: 0.3
phases:
- id: approach_above
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.12
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.03
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.003
      - 0.015
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: grasp_object
- id: grasp_close
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: bilateral_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_up
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_lifted
    when: after_phase
    predicate: object_lifted
    threshold: 0.03
    on_failure: abort
  subtask_id: lift_clearance
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: object_retained
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: abort
  subtask_id: place_at_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.01
    orientation:
      mode: keep_current
  parameters:
    place_force_threshold:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: release_object
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    release_timeout:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **grasp_close** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **lift_up** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_lifted, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.03
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=object_retained, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.02
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_timeout: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: -0.106
- **task_score** (E): 0.268
- **fitness_score**: 0.594  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_above | 1.00 | 0.1482 |
| descend_to_grasp | 1.00 | 0.1005 |
| grasp_close | 1.00 | 0.0111 |
| lift_up | 0.67 | 0.1080 |
| transport_to_goal | 0.67 | 0.2375 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.491, -0.013, 0.158) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.491, -0.013, 0.158)→(0.488, -0.015, 0.057) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 |
| grasp_close | grasp | 1.00 / step_budget | (0.488, -0.015, 0.057)→(0.481, -0.015, 0.049) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 |
| lift_up | lift | 0.67 / step_budget | (0.481, -0.015, 0.049)→(0.477, -0.015, 0.157) | (0.493, -0.015, 0.026)→(0.484, -0.015, 0.126) | 0.281→0.250 |
| transport_to_goal | approach | 0.67 / step_budget | (0.477, -0.015, 0.157)→(0.616, 0.153, 0.242) | (0.484, -0.015, 0.126)→(0.574, 0.067, 0.016) | 0.250→0.198 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.305
- phase_score: 0.552
- phase_breakdown.approach_object_score: 0.436
- phase_breakdown.place_at_goal_score: 0.163
- phase_breakdown.grasp_object_score: 1.000
- phase_breakdown.lift_clearance_score: 0.578
- grasp_place_fitness: 0.609

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.609
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.305
- **Median Q (composite search score)**: -0.114
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.371


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51678,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_z":0.12694,"approach_above.approach_speed":0.20825,"descend_to_grasp.descend_speed":0.05897,"descend_to_grasp.descend_tolerance":0.00616,"descend_to_place.place_force_threshold":4.77627,"descend_to_place.place_speed":0.0726,"lift_up.lift_height":0.1895,"lift_up.lift_speed":0.05118,"release_object.release_timeout":0.56972,"transport_to_goal.transport_speed":0.12869,"transport_to_goal.transport_tolerance":0.0243},"optimized_scores":{"best_composite_score":-0.114,"best_fitness_score":0.586,"best_task_score":0.26051},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":947.0,"contact_point_centroid":[0.58268,0.06921,-0.00317],"force_p95":0.58918,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55137,"mean_force":0.16953,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58921,0.11688,0.25031]},{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.47299,-0.01947,-0.00114],"force_p95":0.23656,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3281,"mean_force":0.06326,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46295,-0.01964,0.05426]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11411.0,"contact_point_centroid":[0.46083,-0.0008,0.09779],"force_p95":0.11009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2854,"mean_force":0.08399,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46061,-0.01956,0.10086]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13555.0,"contact_point_centroid":[0.46003,-0.03811,0.0983],"force_p95":0.10224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2817,"mean_force":0.07182,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46058,-0.01956,0.1018]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3079.0,"contact_point_centroid":[0.49917,0.00154,0.17224],"force_p95":0.13935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26308,"mean_force":0.09417,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4958,0.01968,0.17672]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2678.0,"contact_point_centroid":[0.49951,0.03811,0.17205],"force_p95":0.14469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26202,"mean_force":0.10535,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49584,0.01974,0.17675]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02009,-0.00204],"force_p95":0.13525,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17298,"mean_force":0.12585,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.46554,-0.0197,0.05378]},{"body_a":"world","body_b":"grasp_target","contact_count":1472.0,"contact_point_centroid":[0.47616,-0.02015,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48703,-0.00872,0.23353]},{"body_a":"world","body_b":"grasp_target","contact_count":2136.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47194,-0.01887,0.11195]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2917.0,"contact_point_centroid":[0.46392,-0.00085,0.05054],"force_p95":0.09064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09349,"mean_force":0.07084,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.46447,-0.01967,0.05268]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3439.0,"contact_point_centroid":[0.46443,-0.03853,0.05059],"force_p95":0.08558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08642,"mean_force":0.06106,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.46447,-0.01967,0.05268]},{"body_a":"left_finger","body_b":"right_finger","contact_count":790.0,"contact_point_centroid":[0.59575,0.12343,0.25761],"force_p95":0.01275,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01605,"mean_force":0.01081,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5956,0.12343,0.25537]}],"total_contact_groups":12},"final_pose_error":0.02413,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.58291,0.0693,0.01602],"final_tcp_position":[0.61865,0.14724,0.27339],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.47514,-0.01798,0.16653],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14053,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.47177,-0.01986,0.06024],"tcp_start":[0.47514,-0.01798,0.16653],"tcp_to_object_dist_end":0.0345,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01977,0.02585],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28828,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.46444,-0.01967,0.05265],"tcp_start":[0.47177,-0.01986,0.06024],"tcp_to_object_dist_end":0.02922,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46117,-0.01963,0.11471],"object_pos_start":[0.47609,-0.01977,0.02585],"object_to_goal_dist_end":0.25814,"object_to_goal_dist_start":0.28828,"object_z_max":0.1146,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.46063,-0.01955,0.15028],"tcp_start":[0.46444,-0.01967,0.05265],"tcp_to_object_dist_end":0.03557,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.58291,0.0693,0.01602],"object_pos_start":[0.46117,-0.01963,0.11471],"object_to_goal_dist_end":0.20176,"object_to_goal_dist_start":0.25814,"object_z_max":0.17026,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.61865,0.14724,0.27339],"tcp_start":[0.46063,-0.01955,0.15028],"tcp_to_object_dist_end":0.27128,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62092,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_z":0.1321,"approach_above.approach_speed":0.20233,"descend_to_grasp.descend_speed":0.05123,"descend_to_grasp.descend_tolerance":0.00552,"descend_to_place.place_force_threshold":4.02518,"descend_to_place.place_speed":0.04084,"lift_up.lift_height":0.11468,"lift_up.lift_speed":0.05497,"release_object.release_timeout":0.76,"transport_to_goal.transport_speed":0.14513,"transport_to_goal.transport_tolerance":0.02216},"optimized_scores":{"best_composite_score":-0.0913,"best_fitness_score":0.6087,"best_task_score":0.30539},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1190.0,"contact_point_centroid":[0.55294,0.0816,-0.00278],"force_p95":0.41944,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53931,"mean_force":0.15572,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58107,0.14948,0.19301]},{"body_a":"world","body_b":"grasp_target","contact_count":157.0,"contact_point_centroid":[0.455,-0.02519,-0.00118],"force_p95":0.23277,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31401,"mean_force":0.06039,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44592,-0.02562,0.05426]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12772.0,"contact_point_centroid":[0.44417,-0.04409,0.09992],"force_p95":0.11326,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30303,"mean_force":0.07627,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44352,-0.02551,0.10303]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11658.0,"contact_point_centroid":[0.44465,-0.00684,0.10048],"force_p95":0.11278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2934,"mean_force":0.08282,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44352,-0.02551,0.10345]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3147.0,"contact_point_centroid":[0.48884,0.00973,0.16177],"force_p95":0.13499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26794,"mean_force":0.09769,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48364,0.02781,0.16581]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2735.0,"contact_point_centroid":[0.48746,0.04421,0.16133],"force_p95":0.15458,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24907,"mean_force":0.11161,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48218,0.02593,0.16544]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02626,-0.00205],"force_p95":0.13939,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17996,"mean_force":0.12676,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44841,-0.02572,0.05367]},{"body_a":"world","body_b":"grasp_target","contact_count":1460.0,"contact_point_centroid":[0.45856,-0.02632,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.47945,-0.01138,0.23595]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2663.0,"contact_point_centroid":[0.44804,-0.00687,0.05011],"force_p95":0.10117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1291,"mean_force":0.0761,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44738,-0.02568,0.05265]},{"body_a":"world","body_b":"grasp_target","contact_count":2504.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45545,-0.02466,0.11382]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3199.0,"contact_point_centroid":[0.44794,-0.04441,0.05034],"force_p95":0.09249,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09351,"mean_force":0.06455,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44738,-0.02568,0.05265]},{"body_a":"left_finger","body_b":"right_finger","contact_count":969.0,"contact_point_centroid":[0.58964,0.15989,0.19766],"force_p95":0.01268,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.0108,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58947,0.15989,0.19537]}],"total_contact_groups":12},"final_pose_error":0.02192,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.5529,0.08145,0.01602],"final_tcp_position":[0.61723,0.19448,0.20293],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"phases":[{"n_steps":366.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.45946,-0.02348,0.17138],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14539,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.45445,-0.02595,0.05966],"tcp_start":[0.45946,-0.02348,0.17138],"tcp_to_object_dist_end":0.03389,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02583,0.02581],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30337,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.44735,-0.02568,0.05262],"tcp_start":[0.45445,-0.02595,0.05966],"tcp_to_object_dist_end":0.02904,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44948,-0.02571,0.12209],"object_pos_start":[0.4585,-0.02583,0.02581],"object_to_goal_dist_end":0.29567,"object_to_goal_dist_start":0.30337,"object_z_max":0.122,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.44355,-0.0255,0.15707],"tcp_start":[0.44735,-0.02568,0.05262],"tcp_to_object_dist_end":0.03548,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":705.0,"n_steps_budget":1000.0,"object_pos_end":[0.5529,0.08145,0.01602],"object_pos_start":[0.44948,-0.02571,0.12209],"object_to_goal_dist_end":0.17792,"object_to_goal_dist_start":0.29567,"object_z_max":0.13766,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.61723,0.19448,0.20293],"tcp_start":[0.44355,-0.0255,0.15707],"tcp_to_object_dist_end":0.2277,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6125,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_z":0.09894,"approach_above.approach_speed":0.07164,"descend_to_grasp.descend_speed":0.0623,"descend_to_grasp.descend_tolerance":0.00537,"descend_to_place.place_force_threshold":2.68507,"descend_to_place.place_speed":0.0654,"lift_up.lift_height":0.13712,"lift_up.lift_speed":0.19401,"release_object.release_timeout":0.55678,"transport_to_goal.transport_speed":0.06056,"transport_to_goal.transport_tolerance":0.01473},"optimized_scores":{"best_composite_score":-0.11359,"best_fitness_score":0.58641,"best_task_score":0.23949},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2121.0,"contact_point_centroid":[0.5874,0.04995,-0.00248],"force_p95":0.17167,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70062,"mean_force":0.14367,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59167,0.08862,0.22798]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.542,0.00094,-0.00111],"force_p95":0.25098,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53078,"mean_force":0.06985,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52943,0.00087,0.04449]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8291.0,"contact_point_centroid":[0.53015,0.01976,0.0989],"force_p95":0.10263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37268,"mean_force":0.06767,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52706,0.00084,0.09652]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8562.0,"contact_point_centroid":[0.5302,-0.01803,0.09658],"force_p95":0.1016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33568,"mean_force":0.06601,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.5271,0.00084,0.09456]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3515.0,"contact_point_centroid":[0.54751,0.04123,0.17762],"force_p95":0.16073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23342,"mean_force":0.09855,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54111,0.02264,0.17701]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4407.0,"contact_point_centroid":[0.54824,0.00565,0.17762],"force_p95":0.12429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18244,"mean_force":0.0803,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54204,0.02387,0.17794]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00103,-0.00203],"force_p95":0.13112,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14692,"mean_force":0.12522,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53225,0.00093,0.04428]},{"body_a":"world","body_b":"grasp_target","contact_count":2264.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51714,0.00049,0.21688]},{"body_a":"world","body_b":"grasp_target","contact_count":2164.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53677,0.00101,0.0871]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4166.0,"contact_point_centroid":[0.53153,-0.01829,0.04554],"force_p95":0.07614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10286,"mean_force":0.05135,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53104,0.00091,0.04284]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4827.0,"contact_point_centroid":[0.53157,0.01998,0.04478],"force_p95":0.06822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09303,"mean_force":0.04503,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53104,0.00091,0.04284]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2022.0,"contact_point_centroid":[0.59427,0.09169,0.23275],"force_p95":0.01118,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01646,"mean_force":0.01059,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59405,0.09169,0.2304]}],"total_contact_groups":12},"final_pose_error":0.06762,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.58746,0.04997,0.01602],"final_tcp_position":[0.61342,0.11668,0.25003],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.537,0.001,0.13563],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10985,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":541.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.5391,0.00104,0.0525],"tcp_start":[0.537,0.001,0.13563],"tcp_to_object_dist_end":0.02699,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00085,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25043,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.53101,0.0009,0.04281],"tcp_start":[0.5391,0.00104,0.0525],"tcp_to_object_dist_end":0.02147,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.54247,0.00089,0.1402],"object_pos_start":[0.54421,0.00085,0.02588],"object_to_goal_dist_end":0.19585,"object_to_goal_dist_start":0.25043,"object_z_max":0.14003,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.52731,0.00085,0.16454],"tcp_start":[0.53101,0.0009,0.04281],"tcp_to_object_dist_end":0.02868,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58746,0.04997,0.01602],"object_pos_start":[0.54247,0.00089,0.1402],"object_to_goal_dist_end":0.21439,"object_to_goal_dist_start":0.19585,"object_z_max":0.16605,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.61342,0.11668,0.25003],"tcp_start":[0.52731,0.00085,0.16454],"tcp_to_object_dist_end":0.24471,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```